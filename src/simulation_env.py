from typing import Optional, Union, Tuple, Generator, List, Any, Dict
from datetime import timedelta
import random

import pandas as pd
from gym import spaces
from gym.core import ObsType, ActType

from src.energy_manipulation.production import ProductionSystem
from src.prosumer import Prosumer
from src.battery import Battery
from src.energy_manipulation.energy_systems import EnergySystems
from src.market import EnergyMarket
from src.clock import SimulationClock
from src.constants import *
from src.callback import Callback


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

        self.simulation = self._simulation()
        self.first_actions_scheduled = False
        self.first_actions_set = False

        self.prosumer = self._setup_systems(data_and_callbacks, self._clock)

        # start generator object
        self.simulation.send(None)

    @staticmethod
    def _setup_systems(data_and_callbacks: DfsCallbacksDictType, clock: SimulationClock) -> Prosumer:
        battery = Battery()

        # data_and_callbacks
        # {
        #     'market': (),
        #     'production': [(), ...],
        # }
        systems = []
        for df, callback in data_and_callbacks.get('production', []):
            systems.append(ProductionSystem(df, callback))
        energy_systems = EnergySystems(systems)

        df, callback = data_and_callbacks.get('market', (None, None))
        market = None
        if df is not None:
            market = EnergyMarket(df, callback, clock.view())

        prosumer = Prosumer(battery, energy_systems, energy_market=market)
        return prosumer

    def reset(self, *, seed: Optional[int] = None, return_info: bool = False, options: Optional[dict] = None) -> Union[
        ObsType, Tuple[ObsType, dict]]:
        return np.zeros(self.shape)

    def _observation(self) -> ObservationType:
        return np.zeros(self.shape), 0, False, {}

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
                self._run_in_random_order([
                    (self.prosumer.consume, [self._clock.cur_datetime]),
                    (self.prosumer.produce, [self._clock.cur_datetime]),
                ])

            self._clock.tick()

    @staticmethod
    def _run_in_random_order(functions_and_calldata: List[Tuple[callable, List[Any]]]) -> None:
        random.shuffle(functions_and_calldata)
        for f, args in functions_and_calldata:
            f(*args)

    def render(self, mode="human"):
        pass
