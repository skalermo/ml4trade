from datetime import timedelta
from typing import Tuple, Generator, Dict, List, Any, Optional

from gym import spaces
from gym.core import ObsType, ActType
from gym.utils import seeding

from ml4trade.data_strategies import DataStrategy
from ml4trade.domain.clock import SimulationClock
from ml4trade.domain.constants import *
from ml4trade.domain.consumption import ConsumptionSystem
from ml4trade.domain.market import EnergyMarket, UNSCHEDULED_MULTIPLIER
from ml4trade.domain.production import ProductionSystem
from ml4trade.domain.prosumer import Prosumer
from ml4trade.domain.units import Currency, MWh
from ml4trade.domain.utils import setup_systems
from ml4trade.rendering import render_all as _render_all
from ml4trade.utils import calc_tick_offset, dfs_are_long_enough

ObservationType = Tuple[ObsType, float, bool, dict]
EnvHistory = Dict[str, List[Any]]


class SimulationEnv(gym.Env):
    # immutable properties
    action_space: spaces.Box
    observation_space: spaces.Box
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
    _total_reward: float
    history: EnvHistory
    _simulation: Generator[None, ActType, None]

    def __init__(
            self,
            data_strategies: Dict[str, DataStrategy] = None,
            start_datetime: datetime = START_TIME,
            end_datetime: datetime = END_TIME,
            scheduling_time: time = SCHEDULING_TIME,
            action_replacement_time: time = ACTION_REPLACEMENT_TIME,
            prosumer_init_balance: Currency = Currency(10_000),
            battery_capacity: MWh = MWh(0.1),
            battery_init_charge: MWh = MWh(0.1),
            battery_efficiency: float = 1.0,
            start_tick: int = None,
    ):
        if data_strategies is None:
            data_strategies = {}

        obs_size = sum(map(lambda x: x.observation_size(), data_strategies.values()))
        self.action_space = SIMULATION_ENV_ACTION_SPACE
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(obs_size + 2,), dtype=np.float32)
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
        self._total_reward = 0
        self.history = {key: [] for key in env_history_keys}
        self._simulation = self.__simulation()
        self._simulation.send(None)

        return self._observation()[0]

    def _observation(
            self,
            potential_reward: Optional[float] = None,
            unscheduled_actions_profit: Optional[float] = None,
    ) -> ObservationType:
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
        if potential_reward is None:
            potential_reward = self._calculate_potential_reward()
        if unscheduled_actions_profit is None:
            unscheduled_actions_profit = self._calculate_unscheduled_actions_profit()
        reward = self._calculate_balance_diff() - potential_reward - unscheduled_actions_profit
        done = self._end_datetime <= self._clock.cur_datetime
        return obs, reward, done, {}

    def _calculate_balance_diff(self) -> float:
        return (self._prosumer_balance - self._prev_prosumer_balance).value

    def _calculate_unscheduled_actions_profit(self) -> float:
        prices = self.history['price']
        if len(prices) < 72 - self._clock.scheduling_time.hour:
            return 0
        start_idx = -self._clock.scheduling_time.hour - 24
        end_idx = start_idx + 24
        avg_price = sum(prices[start_idx:end_idx]) / 24

        def sum_unscheduled_amounts(a: List[Tuple[float, bool]]) -> float:
            return sum(map(lambda x: x[0], filter(lambda x: x[1], a)), 0)

        bought = self.history['unscheduled_buy_amounts']
        sold = self.history['unscheduled_sell_amounts']
        total_bought = sum_unscheduled_amounts(bought[start_idx:end_idx])
        total_sold = sum_unscheduled_amounts(sold[start_idx:end_idx])
        unscheduled_profit = total_sold * avg_price / UNSCHEDULED_MULTIPLIER
        unscheduled_profit -= total_bought * avg_price * UNSCHEDULED_MULTIPLIER
        return unscheduled_profit

    def _calculate_potential_reward(self) -> float:
        prices = self.history['price']
        # max amount of time history goes unfilled is
        # 24 - scheduling_hour hours and another 24 hours
        # we need another 24 hours to fill up history
        # with real values
        if len(prices) < 72 - self._clock.scheduling_time.hour:
            return 0
        produced = self.history['energy_produced']
        consumed = self.history['energy_consumed']
        start_idx = -self._clock.scheduling_time.hour - 24
        end_idx = start_idx + 24
        total_energy_produced = sum(produced[start_idx:end_idx])
        total_energy_consumed = sum(consumed[start_idx:end_idx])
        total_extra_energy_produced = total_energy_produced - total_energy_consumed
        avg_price = sum(prices[start_idx:end_idx]) / 24
        return total_extra_energy_produced * avg_price

    def _update_history_for_last_tick(self) -> None:
        self.history['wallet_balance'].append(self._prosumer.wallet.balance.value)
        self.history['tick'].append(self._clock.cur_tick)
        self.history['datetime'].append(self._clock.cur_datetime)
        self.history['energy_produced'].append(self._production_system.ds.last_processed)
        self.history['energy_consumed'].append(self._consumption_system.ds.last_processed)
        self.history['price'].append(self._market.ds.last_processed)
        self.history['scheduled_buy_amounts'].append(self._prosumer.last_scheduled_buy_transaction)
        self.history['scheduled_sell_amounts'].append(self._prosumer.last_scheduled_sell_transaction)
        if self._prosumer.last_unscheduled_buy_transaction is not None:
            self.history['unscheduled_buy_amounts'].append(self._prosumer.last_unscheduled_buy_transaction)
            self._prosumer.last_unscheduled_buy_transaction = None
        else:
            self.history['unscheduled_buy_amounts'].append((0, False))
        if self._prosumer.last_unscheduled_sell_transaction is not None:
            self.history['unscheduled_sell_amounts'].append(self._prosumer.last_unscheduled_sell_transaction)
            self._prosumer.last_unscheduled_sell_transaction = None
        else:
            self.history['unscheduled_sell_amounts'].append((0, False))
        self.history['battery'].append(self._prosumer.battery.rel_current_charge)

    def step(self, action: ActType) -> ObservationType:
        self._simulation.send(action)
        self.history['balance_diff'].append(self._calculate_balance_diff())
        potential_reward = self._calculate_potential_reward()
        self.history['potential_reward'].append(potential_reward)
        unscheduled_actions_profit = self._calculate_unscheduled_actions_profit()
        self.history['unscheduled_actions_profit'].append(unscheduled_actions_profit)
        self.history['action'].append(action.tolist())
        return self._observation(potential_reward, unscheduled_actions_profit)

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

            self._update_history_for_last_tick()
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

    def render_all(self):
        _render_all(self.history)

    def save_history(self, path: str = 'env_history.json'):
        import json

        class CustomEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, np.ndarray):
                    return obj.tolist()
                return json.JSONEncoder.default(self, obj)

        with open(path, 'w') as f:
            json.dump(self.history, f, indent=2, cls=CustomEncoder, default=str)
