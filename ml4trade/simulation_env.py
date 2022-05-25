from typing import Tuple, Generator, Dict, List, Any

from gym import spaces
from gym.core import ObsType, ActType

from ml4trade.consumption import ConsumptionSystem
from ml4trade.production import ProductionSystem
from ml4trade.prosumer import Prosumer
from ml4trade.battery import Battery
from ml4trade.market import EnergyMarket
from ml4trade.clock import SimulationClock
from ml4trade.constants import *
from ml4trade.data_strategies import DataStrategy
from ml4trade.units import Currency, MWh
from ml4trade.utils import run_in_random_order, calc_start_idx, dfs_are_long_enough
from ml4trade.rendering import render_all as _render_all

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
    ):
        if data_strategies is None:
            data_strategies = {}

        obs_size = sum(map(lambda x: x.observation_size(), data_strategies.values()))
        self.action_space = SIMULATION_ENV_ACTION_SPACE
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(obs_size + 1,), dtype=np.float32)
        self._start_tick = calc_start_idx(list(data_strategies.values()), scheduling_time)
        assert dfs_are_long_enough(list(data_strategies.values()), start_datetime, end_datetime, self._start_tick), \
            'Provided dataframe is too short'

        self._start_datetime = start_datetime
        self._end_datetime = end_datetime
        self._prosumer_init_balance = prosumer_init_balance
        self._battery_init_charge = battery_init_charge

        (
            self._clock,
            self._prosumer,
            self._market,
            self._production_system,
            self._consumption_system
        ) = self._setup_systems(data_strategies, self._start_tick, prosumer_init_balance,
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
        self._prosumer.wallet.balance = self._prosumer_init_balance
        self._prosumer.battery.current_charge = self._battery_init_charge
        self._prosumer.scheduled_buy_amounts = None
        self._prosumer.scheduled_sell_amounts = None
        self._prosumer.scheduled_buy_thresholds = None
        self._prosumer.scheduled_sell_thresholds = None
        self._prosumer.next_day_actions = None
        self._clock.cur_datetime = self._start_datetime
        self._clock.cur_tick = self._start_tick
        self._prev_prosumer_balance = self._prosumer_init_balance
        self._first_actions_scheduled = False
        self._first_actions_set = False
        self._total_reward = 0
        self.history = {key: [] for key in env_history_keys}
        self._simulation = self.__simulation()
        self._simulation.send(None)

        return self._observation()[0]

    def _observation(self) -> ObservationType:
        market_obs = self._market.observation()
        production_obs = self._production_system.observation()
        consumption_obs = self._consumption_system.observation()
        obs = [*market_obs, *production_obs, *consumption_obs, self._prosumer.battery.rel_current_charge]
        reward = self._calculate_reward()
        done = self._end_datetime <= self._clock.cur_datetime
        return obs, reward, done, {}

    def _calculate_reward(self) -> float:
        balance_diff = self._prosumer.wallet.balance - self._prev_prosumer_balance
        return balance_diff.value

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
        self._prev_step_prosumer_balance = self._prosumer.wallet.balance
        self._simulation.send(action)
        self._total_reward += self._calculate_reward()
        self.history['total_reward'].append(self._total_reward)
        self.history['action'].append(action)
        return self._observation()

    def __simulation(self) -> Generator[None, ActType, None]:
        while True:
            if self._clock.is_it_scheduling_hour():
                action = yield
                self._prosumer.schedule(action)
                if not self._first_actions_scheduled:
                    self._first_actions_scheduled = True

            if self._clock.is_it_action_replacement_hour() and self._first_actions_scheduled:
                self._prosumer.set_new_actions()
                if not self._first_actions_set:
                    self._first_actions_set = True

            if self._first_actions_set:
                run_in_random_order([self._prosumer.consume, self._prosumer.produce])

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
