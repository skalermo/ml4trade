from datetime import timedelta, datetime
from typing import Tuple, Generator, Union

from gymnasium.core import Wrapper, ObsType
from gymnasium.utils import seeding

from ml4trade.simulation_env import SimulationEnv
from ml4trade.utils import timedelta_to_hours


class IntervalWrapper(Wrapper):
    env: SimulationEnv

    def __init__(self, env: Union[SimulationEnv, Wrapper], interval: timedelta, split_ratio: float = 0.8, randomly_set_battery=False):
        super().__init__(env)

        self.start_datetime = env._start_datetime
        self.end_datetime = env._end_datetime
        self.start_tick = env._start_tick
        self.interval = interval
        self.randomly_set_battery = randomly_set_battery
        self.interval_in_ticks = timedelta_to_hours(interval)
        self.interval_start_ticks = []
        self.train_mode = True
        data_duration = self.end_datetime - self.start_datetime
        self.train_data_duration = data_duration * split_ratio
        self.test_data_start = self.start_datetime + self.train_data_duration
        self.test_data_start_tick = self.start_tick + timedelta_to_hours(self.train_data_duration)
        self._ep_interval_ticks_generator = self.__ep_interval_ticks_generator()

        assert self._is_interval_allowed(interval), \
            f'Max allowed interval is {self.train_data_duration.days} days'

    def _is_interval_allowed(self, interval: timedelta) -> bool:
        return self.train_data_duration >= interval

    def reset(self, **kwargs) -> Tuple[ObsType, dict]:
        seed = kwargs.get('seed')
        if seed is not None:
            self.np_random, seed = seeding.np_random(seed)
            self._ep_interval_ticks_generator = self.__ep_interval_ticks_generator()

        if self.train_mode:
            start_tick = next(self._ep_interval_ticks_generator)
            start_datetime, end_datetime = self._ep_interval_from_start_tick(start_tick)
            self.env._start_datetime = start_datetime
            self.env._end_datetime = end_datetime
            self.env._start_tick = start_tick

        battery_charge_to_set = None
        if self.randomly_set_battery and self.train_mode:
            rand_rel_charge = self.np_random.uniform(0.05, 0.95)
            battery_charge_to_set = self.env._prosumer.battery.capacity * rand_rel_charge

        kwargs['options'] = dict(battery_charge_to_set=battery_charge_to_set)
        return self.env.reset(
            **kwargs
        )

    def __ep_interval_ticks_generator(self) -> Generator[int, None, None]:
        max_offset = self.test_data_start_tick - self.start_tick - self.interval_in_ticks
        while True:
            rand_offset = self.np_random.integers(0, min(self.interval_in_ticks - 1, max_offset),
                                                  size=None, endpoint=True)
            ep_intervals_start_ticks = [start for start in range(
                self.start_tick + rand_offset, self.test_data_start_tick - self.interval_in_ticks + 1,
                self.interval_in_ticks
            )]
            self.interval_start_ticks = ep_intervals_start_ticks
            assert len(ep_intervals_start_ticks) > 0
            self.np_random.shuffle(ep_intervals_start_ticks)
            for i in ep_intervals_start_ticks:
                yield i

    def _ep_interval_from_start_tick(self, tick: int) -> Tuple[datetime, datetime]:
        start_datetime = self.start_datetime + timedelta(hours=tick - self.start_tick)
        end_datetime = start_datetime + self.interval
        return start_datetime, end_datetime

    def set_interval(self, new_interval: timedelta):
        assert self._is_interval_allowed(new_interval), \
            f'Max allowed interval is {self.train_data_duration.days} days'

        self.interval = new_interval
        self.interval_in_ticks = timedelta_to_hours(new_interval)
        self._ep_interval_ticks_generator = self.__ep_interval_ticks_generator()
