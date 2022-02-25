from typing import Optional, Union, Tuple
from enum import Enum

import gym
import numpy as np
from gym import spaces
from gym.core import ObsType, ActType


class Actions(Enum):
    Sell = 0
    Buy = 1


class SimulationEnv(gym.Env):
    def __init__(self):
        self.action_space = spaces.Discrete(len(Actions))
        self.shape = (1, 1)
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=self.shape, dtype=np.float32)

    def step(self, action: ActType) -> Tuple[ObsType, float, bool, dict]:
        return np.zeros(self.shape), 0, False, {}

    def reset(self, *, seed: Optional[int] = None, return_info: bool = False, options: Optional[dict] = None) -> Union[
            ObsType, Tuple[ObsType, dict]]:
        return np.zeros(self.shape)

    def render(self, mode="human"):
        pass
