from datetime import timedelta, datetime
from typing import Tuple, Generator, Union

from gym.core import Wrapper, ObsType
from gym.utils import seeding

from ml4trade.simulation_env import SimulationEnv
from ml4trade.utils import timedelta_to_hours


class IntervalWrapper(Wrapper):
    env: SimulationEnv

    def __init__(self, env: Union[SimulationEnv, Wrapper], interval: timedelta, split_ratio: float = 0.8):
        super().__init__(env)

        self.start_datetime = env._start_datetime
        self.end_datetime = env._end_datetime
        self.start_tick = env._start_tick
        self.interval = interval
        self.interval_in_ticks = timedelta_to_hours(interval)
        self.train_mode = True
        self._ep_interval_ticks_generator = self.__ep_interval_ticks_generator()

        data_duration = self.end_datetime - self.start_datetime
        train_data_duration = data_duration * split_ratio
        self.test_data_start = self.start_datetime + train_data_duration
        self.test_data_start_tick = timedelta_to_hours(train_data_duration)

    def reset(self, **kwargs) -> ObsType:
        seed = kwargs.get('seed')
        if seed is not None:
            self._np_random, seed = seeding.np_random(seed)

        if self.train_mode:
            start_tick = next(self._ep_interval_ticks_generator)
            start_datetime, end_datetime = self._ep_interval_from_start_tick(start_tick)
            self.env._start_datetime = start_datetime
            self.env._end_datetime = end_datetime
            self.env._start_tick = start_tick
        return self.env.reset(**kwargs)

    def __ep_interval_ticks_generator(self) -> Generator[int, None, None]:
        while True:
            rand_offset = self.np_random.integers(0, self.interval_in_ticks - 1, size=None)
            ep_intervals_start_ticks = [start for start in range(
                self.start_tick + rand_offset, self.test_data_start_tick - self.interval_in_ticks + 1,
                self.interval_in_ticks
            )]
            self.np_random.shuffle(ep_intervals_start_ticks)
            for i in ep_intervals_start_ticks:
                yield i

    def _ep_interval_from_start_tick(self, tick: int) -> Tuple[datetime, datetime]:
        start_datetime = self.start_datetime + timedelta(hours=tick - self.start_tick)
        end_datetime = start_datetime + self.interval
        return start_datetime, end_datetime

    # def set_to_test_and_reset(self) -> ObsType:
    #     self.train_mode = False
    #     self.env._start_datetime = self.test_data_start
    #     self.env._end_datetime = self.end_datetime
    #     self.env._start_tick = self.test_data_start_tick
    #     return self.env.reset()
