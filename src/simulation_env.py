from typing import Optional, Union, Tuple, Generator
from datetime import datetime, timedelta, time

import numpy as np
import gym
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

TRADE_AMOUNT_BOUND_LOW = -np.inf
TRADE_AMOUNT_BOUND_HIGH = np.inf
PRICE_THRESHOLD_MAX = np.inf


class SimulationEnv(gym.Env):
    def __init__(
            self,
            start_datetime: datetime = START_TIME,
            scheduling_time: time = SCHEDULING_TIME,
            action_replacement_time: time = ACTION_REPLACEMENT_TIME
    ):
        self.action_space = self._action_space()
        self.shape = (1, 1)
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=self.shape, dtype=np.float32)
        self.cur_datetime = start_datetime
        self.scheduling_time = scheduling_time
        self.action_replacement_time = action_replacement_time
        self.simulation = self._simulation()

        battery = Battery()
        energy_systems = EnergySystems()
        self.prosumer = Prosumer(battery, energy_systems)

        # start generator object
        self.simulation.send(None)

    @staticmethod
    def _action_space() -> spaces.Box:
        # Action space of 24 energy amounts to trade and 24 price thresholds.
        # Defines transactions for each hour for the next 24 hours
        # starting from ACTION_REPLACEMENT_TIME
        return spaces.Box(
            low=np.array([TRADE_AMOUNT_BOUND_LOW] * 24 + [0] * 24),
            high=np.array([TRADE_AMOUNT_BOUND_HIGH] * 24 + [PRICE_THRESHOLD_MAX] * 24)
        )

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

    def _observation(self) -> ObservationType:
        return np.zeros(self.shape), 0, False, {}

    def step(self, action: ActType) -> ObservationType:
        return self.simulation.send(action)

    def _simulation(self) -> Generator[ObservationType, ActType, None]:
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
