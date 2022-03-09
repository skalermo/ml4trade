from typing import Optional, Union, Tuple, Generator
from enum import Enum
from datetime import datetime, timedelta, time

import gym
import numpy as np
from gym import spaces
from gym.core import ObsType, ActType

from src.prosumer import Prosumer
from src.battery import Battery
from src.energy_manipulation.energy_systems import EnergySystems


ObservationType = Tuple[ObsType, float, bool, dict]

SCHEDULING_TIME = time(hour=10, minute=30)
ACTION_REPLACEMENT_TIME = time(hour=0)  # midnight
START_TIME = datetime(
    year=2022,
    month=3,
    day=8,
    hour=SCHEDULING_TIME.hour,
)


class Actions(Enum):
    Sell = 0
    Buy = 1


class SimulationEnv(gym.Env):
    def __init__(
            self,
            start_datetime: datetime = START_TIME,
            scheduling_time: time = SCHEDULING_TIME,
            action_replacement_time: time = ACTION_REPLACEMENT_TIME):
        self.action_space = spaces.Discrete(len(Actions))
        self.shape = (1, 1)
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=self.shape, dtype=np.float32)
        self.cur_datetime = start_datetime
        self.scheduling_time = scheduling_time
        self.action_replacement_time = action_replacement_time
        self.simulation = self._simulation()
        self.simulation.send(None)

        battery = Battery()
        energy_systems = EnergySystems()
        self.prosumer = Prosumer(battery, energy_systems)

    def reset(self, *, seed: Optional[int] = None, return_info: bool = False, options: Optional[dict] = None) -> Union[
        ObsType, Tuple[ObsType, dict]]:
        return np.zeros(self.shape)

    def _observation(self) -> ObservationType:
        return np.zeros(self.shape), 0, False, {}

    def step(self, action: ActType) -> ObservationType:
        return self.simulation.send(action)

    def _simulation(self) -> Generator[ObservationType, ActType, None]:
        yield
        while True:
            if self.is_now_scheduling_time():
                action = yield self._observation()
                self.prosumer.schedule(action)

            if self.is_now_action_replacement_time():
                self.prosumer.set_new_actions()

            # self.prosumer.consume_energy()
            # self.prosumer.produce_energy()

            self.cur_datetime += timedelta(hours=1)

    def render(self, mode="human"):
        pass

    def is_now_scheduling_time(self) -> bool:
        return self.cur_datetime.time().hour == self.scheduling_time.hour

    def is_now_action_replacement_time(self) -> bool:
        return self.cur_datetime.time().hour == self.action_replacement_time.hour
