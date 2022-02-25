from typing import Optional, Union, Tuple
from enum import Enum

import gym
import numpy as np
from gym import spaces
from gym.core import ObsType, ActType

from src.prosumer import Prosumer
from src.battery import Battery
from src.energy_manipulation.energy_systems import EnergySystems


class Actions(Enum):
    Sell = 0
    Buy = 1


class SimulationEnv(gym.Env):
    def __init__(self):
        self.action_space = spaces.Discrete(len(Actions))
        self.shape = (1, 1)
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=self.shape, dtype=np.float32)

        battery = Battery()
        energy_systems = EnergySystems()
        self.prosumer = Prosumer(battery, energy_systems)

    def step(self, action: ActType) -> Tuple[ObsType, float, bool, dict]:
        self.prosumer.schedule(action)
        self._simulate_day()
        return np.zeros(self.shape), 0, False, {}

    def _simulate_day(self):
        midnight = 0
        for hour in range(1, 24 + 1):
            if hour == midnight:
                self.prosumer.set_new_actions()
            self.prosumer.consume_energy()
            self.prosumer.produce_energy()
            self.prosumer.send_transaction()

    def reset(self, *, seed: Optional[int] = None, return_info: bool = False, options: Optional[dict] = None) -> Union[
            ObsType, Tuple[ObsType, dict]]:
        return np.zeros(self.shape)

    def render(self, mode="human"):
        pass
