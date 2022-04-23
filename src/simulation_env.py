from typing import Optional, Union, Tuple, Generator, List, Dict
from datetime import timedelta
import itertools

import pandas as pd
from gym import spaces
from gym.core import ObsType, ActType

from gym_anytrading.envs import TradingEnv

from src.energy_manipulation.consumption import ConsumptionSystem
from src.energy_manipulation.production import ProductionSystem
from src.prosumer import Prosumer
from src.battery import Battery
from src.energy_manipulation.energy_systems import EnergySystems
from src.market import EnergyMarket
from src.clock import SimulationClock
from src.constants import *
from src.callback import Callback
from src.utils import run_in_random_order

ObservationType = Tuple[ObsType, float, bool, dict]
DfsCallbacksType = Tuple[pd.DataFrame, Callback]
DfsCallbacksDictType = Dict[str, Union[DfsCallbacksType, List[DfsCallbacksType]]]


class SimulationEnv(gym.Env):
    def __init__(
            self,
            data_and_callbacks: DfsCallbacksDictType = None,
            start_datetime: datetime = START_TIME,
            scheduling_time: time = SCHEDULING_TIME,
            action_replacement_time: time = ACTION_REPLACEMENT_TIME,
    ):
        if data_and_callbacks is None:
            data_and_callbacks = {}

        self.action_space = SIMULATION_ENV_ACTION_SPACE
        self.shape = (1, 1)
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=self.shape, dtype=np.float32)

        self._clock = SimulationClock(
            start_datetime=start_datetime,
            scheduling_time=scheduling_time,
            action_replacement_time=action_replacement_time,
            start_tick=0,
            tick_duration=timedelta(hours=1)
        )

        self.prosumer, self.market, self.energy_systems = self._setup_systems(data_and_callbacks, self._clock)
        self.prev_prosumer_balance = self.prosumer.wallet.balance

        self.first_actions_scheduled = False
        self.first_actions_set = False
        self.simulation = self._simulation()

        # start generator object
        self.simulation.send(None)

    @staticmethod
    def _setup_systems(data_and_callbacks: DfsCallbacksDictType, clock: SimulationClock) -> Tuple[Prosumer, EnergyMarket, EnergySystems]:
        battery = Battery()

        # data_and_callbacks
        # {
        #     'market': (),
        #     'production': [(), ...],
        # }
        systems = []
        for df, callback in data_and_callbacks.get('production', []):
            systems.append(ProductionSystem(df, callback))

        systems.append(ConsumptionSystem(clock.view()))

        energy_systems = EnergySystems(systems)

        df, callback = data_and_callbacks.get('market', (None, None))
        market = None
        if df is not None:
            market = EnergyMarket(df, callback, clock.view())

        prosumer = Prosumer(battery, energy_systems,
                            clock_view=clock.view(), energy_market=market)
        return prosumer, market, energy_systems

    def reset(self, *, seed: Optional[int] = None, return_info: bool = False, options: Optional[dict] = None) -> Union[
        ObsType, Tuple[ObsType, dict]]:
        return np.zeros(self.shape)

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
        systems_obs = self.energy_systems.observation()
        obs = list(itertools.chain.from_iterable([market_obs, systems_obs]))
        reward = self.prosumer.wallet.balance - self.prev_prosumer_balance
        self.prev_prosumer_balance = self.prosumer.wallet.balance
        return obs, reward, False, {}

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

    # def get_end_tick(self, dfs: List[pd.DataFrame]) -> int:
    #     return self._clock.get_end_tick()
