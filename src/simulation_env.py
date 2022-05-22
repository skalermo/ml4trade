from typing import Tuple, Generator, Dict, List, Any

from gym import spaces
from gym.core import ObsType, ActType

from src.battery import Battery
from src.clock import SimulationClock
from src.constants import *
from src.consumption import ConsumptionSystem
from src.data_strategies.base import DataStrategy
from src.market import EnergyMarket
from src.production import ProductionSystem
from src.prosumer import Prosumer
from src.units import Currency, MWh
from src.utils import run_in_random_order, timedelta_to_hours
from src.rendering import render_all as _render_all

ObservationType = Tuple[ObsType, float, bool, dict]
EnvHistory = Dict[str, List[Any]]


class SimulationEnv(gym.Env):
    # immutable properties
    action_space: spaces.Box
    observation_space: spaces.Box
    start_tick: int
    start_datetime: datetime
    end_datetime: datetime
    prosumer_init_balance: Currency
    battery_init_charge: MWh
    _clock: SimulationClock
    prosumer: Prosumer
    market: EnergyMarket
    production_system: ProductionSystem
    consumption_system: ConsumptionSystem
    # resetable properties
    prev_step_prosumer_balance: Currency
    first_actions_scheduled: bool
    first_actions_set: bool
    total_reward: float
    history: EnvHistory
    simulation: Generator[None, ActType, None]

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
    ):
        if data_strategies is None:
            data_strategies = {}

        obs_size = sum(map(lambda x: x.observation_size(), data_strategies.values()))
        self.action_space = SIMULATION_ENV_ACTION_SPACE
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(obs_size + 1,), dtype=np.float32)
        self.start_tick = max([s.observation_size() for s in data_strategies.values()
                               if s.window_direction == 'backward'])

        dfs_lengths = [len(s.df) for s in data_strategies.values() if s.df is not None]
        episode_hour_length = timedelta_to_hours(end_datetime - start_datetime)
        assert episode_hour_length + 2 * self.start_tick <= min(dfs_lengths), 'Provided dataframe is too short'

        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.prosumer_init_balance = prosumer_init_balance
        self.battery_init_charge = battery_init_charge

        (
            self._clock,
            self.prosumer,
            self.market,
            self.production_system,
            self.consumption_system
        ) = self._setup_systems(data_strategies, self.start_tick, prosumer_init_balance,
                                start_datetime, scheduling_time, action_replacement_time,
                                battery_init_charge, battery_efficiency, battery_capacity)
        self.reset()

    @staticmethod
    def _setup_systems(
            data_strategies: Dict[str, DataStrategy],
            start_tick: int,
            prosumer_init_balance: Currency,
            start_datetime: datetime,
            scheduling_time: time,
            action_replacement_time: time,
            battery_init_charge: MWh,
            battery_efficiency: float,
            battery_capacity: MWh,
    ) -> Tuple[SimulationClock, Prosumer, EnergyMarket, ProductionSystem, ConsumptionSystem]:
        clock = SimulationClock(start_datetime, scheduling_time, action_replacement_time, start_tick)
        battery = Battery(battery_capacity, battery_efficiency, battery_init_charge)

        production_system = ProductionSystem(data_strategies.get('production'), clock.view())
        consumption_system = ConsumptionSystem(data_strategies.get('consumption'), clock.view())
        market = EnergyMarket(data_strategies.get('market'), clock.view())

        prosumer = Prosumer(battery, production_system, consumption_system,
                            clock.view(), prosumer_init_balance, market)
        return clock, prosumer, market, production_system, consumption_system

    def reset(self, **kwargs) -> ObsType:
        self.prosumer.wallet.balance = self.prosumer_init_balance
        self.prosumer.battery.current_charge = self.battery_init_charge
        self.prosumer.scheduled_buy_amounts = None
        self.prosumer.scheduled_sell_amounts = None
        self.prosumer.scheduled_buy_thresholds = None
        self.prosumer.scheduled_sell_thresholds = None
        self.prosumer.next_day_actions = None
        self._clock.cur_datetime = self.start_datetime
        self._clock.cur_tick = self.start_tick
        self.prev_step_prosumer_balance = self.prosumer_init_balance
        self.first_actions_scheduled = False
        self.first_actions_set = False
        self.total_reward = 0
        self.history = {key: [] for key in env_history_keys}
        self.simulation = self._simulation()
        self.simulation.send(None)

        return self._observation()[0]

    def _observation(self) -> ObservationType:
        market_obs = self.market.observation()
        production_obs = self.production_system.observation()
        consumption_obs = self.consumption_system.observation()
        obs = [*market_obs, *production_obs, *consumption_obs, self.prosumer.battery.rel_current_charge]
        reward = self._calculate_reward()
        done = self.end_datetime <= self._clock.cur_datetime
        return obs, reward, done, {}

    def _calculate_reward(self) -> float:
        balance_diff = self.prosumer.wallet.balance - self.prev_step_prosumer_balance
        return balance_diff.value

    def _update_history_for_last_tick(self) -> None:
        self.history['wallet_balance'].append(self.prosumer.wallet.balance.value)
        self.history['tick'].append(self._clock.cur_tick)
        self.history['datetime'].append(self._clock.cur_datetime)
        self.history['energy_produced'].append(self.production_system.ds.last_processed)
        self.history['energy_consumed'].append(self.consumption_system.ds.last_processed)
        self.history['price'].append(self.market.ds.last_processed)
        self.history['scheduled_buy_amounts'].append(self.prosumer.last_scheduled_buy_transaction)
        self.history['scheduled_sell_amounts'].append(self.prosumer.last_scheduled_sell_transaction)
        if self.prosumer.last_unscheduled_buy_transaction is not None:
            self.history['unscheduled_buy_amounts'].append(self.prosumer.last_unscheduled_buy_transaction)
            self.prosumer.last_unscheduled_buy_transaction = None
        else:
            self.history['unscheduled_buy_amounts'].append((0, False))
        if self.prosumer.last_unscheduled_sell_transaction is not None:
            self.history['unscheduled_sell_amounts'].append(self.prosumer.last_unscheduled_sell_transaction)
            self.prosumer.last_unscheduled_sell_transaction = None
        else:
            self.history['unscheduled_sell_amounts'].append((0, False))
        self.history['battery'].append(self.prosumer.battery.rel_current_charge)

    def step(self, action: ActType) -> ObservationType:
        self.prev_step_prosumer_balance = self.prosumer.wallet.balance
        self.simulation.send(action)
        self.total_reward += self._calculate_reward()
        self.history['total_reward'].append(self.total_reward)
        self.history['action'].append(action)
        return self._observation()

    def _simulation(self) -> Generator[None, ActType, None]:
        while True:
            if self._clock.is_it_scheduling_hour():
                action = yield
                self.prosumer.schedule(action)
                if not self.first_actions_scheduled:
                    self.first_actions_scheduled = True

            if self._clock.is_it_action_replacement_hour() and self.first_actions_scheduled:
                self.prosumer.set_new_actions()
                if not self.first_actions_set:
                    self.first_actions_set = True

            if self.first_actions_set:
                run_in_random_order([self.prosumer.consume, self.prosumer.produce])

            self._update_history_for_last_tick()
            self._clock.tick()

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
