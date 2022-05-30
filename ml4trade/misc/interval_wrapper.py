from datetime import timedelta, datetime
from typing import Tuple, Generator
import random

import gym
from gym.core import ObsType, ActType

from ml4trade.simulation_env import SimulationEnv
from ml4trade.utils import timedelta_to_hours


class EnvIntervalWrapper(gym.Env):
    def __init__(self, env: SimulationEnv, interval: timedelta, split_ratio: float = 0.8):
        self.env = env
        self.start_datetime = env._start_datetime
        self.end_datetime = env._end_datetime
        self.min_tick = self.env._start_tick
        self.interval = interval
        self.interval_in_ticks = timedelta_to_hours(interval)
        self.test_mode = False
        self._ep_interval_ticks_generator = self.__ep_interval_ticks_generator()

        data_duration = self.end_datetime - self.start_datetime
        train_data_duration = data_duration * split_ratio
        self.test_data_start = self.start_datetime + train_data_duration
        self.test_data_start_tick = timedelta_to_hours(train_data_duration)

    @property
    def observation_space(self):
        return self.env.observation_space

    @property
    def action_space(self):
        return self.env.action_space

    @property
    def history(self):
        return self.env.history

    def save_history(self, *args, **kwargs):
        self.env.save_history(*args, **kwargs)

    def set_to_test_and_reset(self) -> ObsType:
        self.test_mode = True
        self.env._start_datetime = self.test_data_start
        self.env._end_datetime = self.end_datetime
        self.env._start_tick = self.test_data_start_tick
        return self.env.reset()

    def __ep_interval_ticks_generator(self) -> Generator[int, None, None]:
        ep_intervals_start_ticks = [start for start in range(
            self.min_tick, self.test_data_start_tick - self.interval_in_ticks + 1, self.interval_in_ticks
        )]
        while True:
            start_ticks_shuffled = ep_intervals_start_ticks.copy()
            random.shuffle(start_ticks_shuffled)
            for i in start_ticks_shuffled:
                yield i

    def _ep_interval_from_start_tick(self, tick: int) -> Tuple[datetime, datetime]:
        start_datetime = self.start_datetime + timedelta(hours=tick - self.min_tick)
        end_datetime = start_datetime + self.interval
        return start_datetime, end_datetime

    def step(self, action: ActType) -> Tuple[ObsType, float, bool, dict]:
        return self.env.step(action)

    def reset(self, **kwargs) -> ObsType:
        if not self.test_mode:
            start_tick = next(self._ep_interval_ticks_generator)
            start_datetime, end_datetime = self._ep_interval_from_start_tick(start_tick)
            self.env._start_datetime = start_datetime
            self.env._end_datetime = end_datetime
            self.env._start_tick = start_tick
        return self.env.reset()

    def render(self, *args, **kwargs):
        self.env.render(*args, **kwargs)

    def render_all(self):
        self.env.render_all()
