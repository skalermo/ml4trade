from typing import Tuple, Generator, Dict
from datetime import timedelta
import itertools

from gym import spaces
from gym.core import ObsType, ActType

from src.consumption import ConsumptionSystem
from src.production import ProductionSystem
from src.prosumer import Prosumer
from src.battery import Battery
from src.market import EnergyMarket
from src.clock import SimulationClock
from src.constants import *
from src.data_strategies.base import DataStrategy
from src.custom_types import Currency, kWh
from src.utils import run_in_random_order

ObservationType = Tuple[ObsType, float, bool, dict]


class SimulationEnv(gym.Env):
    def __init__(
            self,
            data_strategies: Dict[str, DataStrategy] = None,
            start_datetime: datetime = START_TIME,
            scheduling_time: time = SCHEDULING_TIME,
            action_replacement_time: time = ACTION_REPLACEMENT_TIME,
            start_tick: int = 0,
            end_tick: int = 10_000,
    ):
        if data_strategies is None:
            data_strategies = {}

        self._clock = SimulationClock(
            start_datetime=start_datetime,
            scheduling_time=scheduling_time,
            action_replacement_time=action_replacement_time,
            start_tick=start_tick,
            tick_duration=timedelta(hours=1),
        )
        self.start_datetime = start_datetime
        self.start_tick = start_tick
        self.end_tick = end_tick

        self.prosumer, self.market, self.production_system, self.consumption_system = self._setup_systems(data_strategies, self._clock)
        self.prev_prosumer_balance = self.prosumer.wallet.balance

        obs_size = 0
        for s in data_strategies.values():
            obs_size += s.window_size()
        self.action_space = SIMULATION_ENV_ACTION_SPACE
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(obs_size,), dtype=np.float32)

        self.first_actions_scheduled = False
        self.first_actions_set = False
        self.simulation = self._simulation()

        # start generator object
        self.simulation.send(None)

    @staticmethod
    def _setup_systems(data_strategies: Dict[str, DataStrategy], clock: SimulationClock)\
            -> Tuple[Prosumer, EnergyMarket, ProductionSystem, ConsumptionSystem]:
        battery = Battery()

        production_system = ProductionSystem(data_strategies.get('production'), clock.view())
        consumption_system = ConsumptionSystem(clock.view())

        market = EnergyMarket(data_strategies.get('market'), clock.view())

        prosumer = Prosumer(battery, production_system, consumption_system,
                            clock_view=clock.view(), energy_market=market)
        return prosumer, market, production_system, consumption_system

    def reset(self, **kwargs) -> ObsType:
        self.prosumer.wallet.balance = Currency(10_000)
        self.prosumer.battery.current_charge = kWh(0)
        self._clock.cur_datetime = self.start_datetime
        self._clock.cur_tick = self.start_tick

        return self._observation()[0]

    def _observation(self) -> ObservationType:
        # obs:
        # - history prices window (1 day backwards) - 24 floats
        # - households energy consumption (1 day backwards) - 24 floats
        # - weather forecast (1 day ahead) - some weather data tuple * 24
        # reward:
        # - cur balance - prev balance
        # done:
        # - if in any of the dfs the end of the data is reached
        #   (need to find overlapping timestamps and common start time)
        # additional info:
        # - idk, no for now
        market_obs = self.market.observation()
        production_obs = self.production_system.observation()
        consumption_obs = self.consumption_system.observation()
        obs = list(itertools.chain.from_iterable([market_obs, production_obs, consumption_obs]))
        reward = (self.prosumer.wallet.balance - self.prev_prosumer_balance).value
        self.prev_prosumer_balance = self.prosumer.wallet.balance
        done = self._clock.cur_tick >= self.end_tick
        return obs, reward, done, {}

    def step(self, action: ActType) -> ObservationType:
        return self.simulation.send(action)

    def _simulation(self) -> Generator[ObservationType, ActType, None]:
        while True:
            if self._clock.is_it_scheduling_hour():
                action = yield self._observation()
                self.prosumer.schedule(action)
                if not self.first_actions_scheduled:
                    self.first_actions_scheduled = True

            if self._clock.is_it_action_replacement_hour() and self.first_actions_scheduled:
                self.prosumer.set_new_actions()
                if not self.first_actions_set:
                    self.first_actions_set = True

            if self.first_actions_set:
                run_in_random_order([self.prosumer.consume, self.prosumer.produce])

            self._clock.tick()

    def render(self, mode="human"):
        pass
