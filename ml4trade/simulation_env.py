from datetime import timedelta, time, datetime
from typing import Tuple, Generator, Dict

import numpy as np
import gym
from gym.core import ObsType, ActType
from gym.utils import seeding

from ml4trade.data_strategies import DataStrategy
from ml4trade.domain.clock import SimulationClock
from ml4trade.domain.constants import (
    START_TIME,
    END_TIME,
    SCHEDULING_TIME,
    ACTION_REPLACEMENT_TIME,
    SIMULATION_ENV_ACTION_SPACE,
)
from ml4trade.domain.consumption import ConsumptionSystem
from ml4trade.domain.market import EnergyMarket
from ml4trade.domain.production import ProductionSystem
from ml4trade.domain.prosumer import Prosumer
from ml4trade.domain.units import Currency, MWh
from ml4trade.domain.utils import setup_systems
from ml4trade.utils import calc_tick_offset, dfs_are_long_enough
from ml4trade.history import History

ObservationType = Tuple[ObsType, float, bool, dict]


class SimulationEnv(gym.Env):
    # immutable properties
    action_space: gym.spaces.Box
    observation_space: gym.spaces.Box
    _start_tick: int
    _start_datetime: datetime
    _end_datetime: datetime
    _prosumer_init_balance: Currency
    _battery_init_charge: MWh
    _clock: SimulationClock
    _prosumer: Prosumer
    _market: EnergyMarket
    _production_system: ProductionSystem
    _consumption_system: ConsumptionSystem
    # resetable properties
    _prev_prosumer_balance: Currency
    _prosumer_balance: Currency
    _first_actions_scheduled: bool
    _first_actions_set: bool
    history: History
    _simulation: Generator[None, ActType, None]

    def __init__(
            self,
            data_strategies: Dict[str, DataStrategy],
            start_datetime: datetime,
            end_datetime: datetime,
            scheduling_time: time,
            action_replacement_time: time,
            prosumer_init_balance: Currency,
            battery_capacity: MWh,
            battery_init_charge: MWh,
            battery_efficiency: float,
            start_tick: int = None,
    ):
        if data_strategies is None:
            data_strategies = {}

        obs_size = sum(map(lambda x: x.observation_size(), data_strategies.values()))
        self.action_space = SIMULATION_ENV_ACTION_SPACE
        self.observation_space = gym.spaces.Box(low=-np.inf, high=np.inf, shape=(obs_size + 2,), dtype=np.float32)
        if start_tick is None:
            start_tick = calc_tick_offset(list(data_strategies.values()), scheduling_time)
        self._start_tick = start_tick
        assert dfs_are_long_enough(list(data_strategies.values()), start_datetime, end_datetime, self._start_tick), \
            'Provided dataframe is too short'

        self._start_datetime = start_datetime + timedelta(hours=self._start_tick)
        self._end_datetime = end_datetime
        self._prosumer_init_balance = prosumer_init_balance
        self._battery_init_charge = battery_init_charge

        (
            self._clock,
            self._prosumer,
            self._market,
            self._production_system,
            self._consumption_system
        ) = setup_systems(data_strategies, self._start_tick, prosumer_init_balance,
                          start_datetime, scheduling_time, action_replacement_time,
                          battery_init_charge, battery_efficiency, battery_capacity)
        self.reset()

    def reset(self, **kwargs) -> ObsType:
        seed = kwargs.get('seed')
        if seed is not None:
            self._np_random, seed = seeding.np_random(seed)

        self._prosumer.wallet.balance = self._prosumer_init_balance
        self._prosumer.battery.current_charge = self._battery_init_charge
        self._prosumer.scheduled_buy_amounts = None
        self._prosumer.scheduled_sell_amounts = None
        self._prosumer.scheduled_buy_thresholds = None
        self._prosumer.scheduled_sell_thresholds = None
        self._prosumer.next_day_actions = None
        self._clock.cur_datetime = self._start_datetime
        self._clock.cur_tick = self._start_tick
        self._prosumer_balance = self._prosumer_init_balance
        self._prev_prosumer_balance = self._prosumer_init_balance
        self._first_actions_scheduled = False
        self._first_actions_set = False
        self.history = History(self._clock.view())
        self._simulation = self.__simulation()
        self._simulation.send(None)

        return self._observation()[0]

    def _observation(self) -> ObservationType:
        market_obs = self._market.observation()
        production_obs = self._production_system.observation()
        consumption_obs = self._consumption_system.observation()
        rel_battery_charge_at_midnight = self._dry_simulation(24 - self._clock.scheduling_time.hour)
        obs = [
            *market_obs,
            *production_obs,
            *consumption_obs,
            self._prosumer.battery.rel_current_charge,
            rel_battery_charge_at_midnight,
        ]
        reward = self._calculate_reward()
        done = self._end_datetime <= self._clock.cur_datetime
        return obs, reward, done, {}

    def _calculate_reward(self) -> float:
        return self._calculate_balance_diff() - self.history.last_day_potential_profit()

    def _calculate_balance_diff(self) -> float:
        return (self._prosumer_balance - self._prev_prosumer_balance).value

    def step(self, action: ActType) -> ObservationType:
        self._simulation.send(action)
        self.history.step_update(action, self._calculate_balance_diff())
        obs, reward, done, info = self._observation()
        self.history.save_reward(reward)
        return obs, reward, done, info

    def _rand_produce_consume(self):
        fs = [self._prosumer.consume, self._prosumer.produce]
        self.np_random.shuffle(fs)
        for f in fs:
            f()

    def __simulation(self) -> Generator[None, ActType, None]:
        while True:
            if self._clock.is_it_scheduling_hour():
                action = yield
                self._prosumer.schedule(action)
                if not self._first_actions_scheduled:
                    self._first_actions_scheduled = True

            if self._clock.is_it_action_replacement_hour() and self._first_actions_scheduled:
                self._prosumer.set_new_actions()
                self._prev_prosumer_balance = self._prosumer_balance
                self._prosumer_balance = self._prosumer.wallet.balance
                if not self._first_actions_set:
                    self._first_actions_set = True

            if self._first_actions_set:
                self._rand_produce_consume()

            self.history.tick_update(
                self._prosumer,
                self._market,
                self._production_system,
                self._consumption_system,
            )
            self._clock.tick()

    def _dry_simulation(self, ticks: int) -> MWh:
        if not self._first_actions_set:
            return self._prosumer.battery.rel_current_charge
        saved_state = (
            self._prosumer.wallet.balance,
            self._prosumer.battery.current_charge,
            self._clock.cur_datetime,
            self._clock.cur_tick
        )
        for _ in range(ticks):
            self._rand_produce_consume()
            self._clock.tick()
        predicted_rel_battery_charge = self._prosumer.battery.rel_current_charge
        (
            self._prosumer.wallet.balance,
            self._prosumer.battery.current_charge,
            self._clock.cur_datetime,
            self._clock.cur_tick
        ) = saved_state
        return predicted_rel_battery_charge

    def render(self, mode="human"):
        NotImplemented('Use render_all()!')

    def render_all(self, last_n_days: int = 2, save_path=None):
        self.history.render(last_n_days, save_path)

    def save_history(self):
        self.history.save()
