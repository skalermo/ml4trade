import unittest
from datetime import timedelta
from collections import Counter

from ml4trade.simulation_env import SimulationEnv
from ml4trade.constants import START_TIME
from ml4trade.misc.interval_wrapper import EnvIntervalWrapper
from ml4trade.utils import timedelta_to_hours
from utils import setup_default_data_strategies


class TestIntervalWrapper(unittest.TestCase):
    def setUp(self) -> None:
        self.end_datetime = START_TIME + timedelta(days=14)
        self.env = SimulationEnv(setup_default_data_strategies(), start_datetime=START_TIME, end_datetime=self.end_datetime)
        self.env_wrapper = EnvIntervalWrapper(env=self.env, interval=timedelta(days=1), split_ratio=0.75)
        data_duration = timedelta(days=14) - timedelta(hours=34)
        self.data_start_tick = timedelta_to_hours(data_duration * 0.75)

    def test_constructor(self):
        self.assertEqual(self.env_wrapper.env, self.env)
        self.assertEqual(self.env_wrapper.start_datetime, START_TIME + timedelta(hours=34))
        self.assertEqual(self.env_wrapper.end_datetime, self.end_datetime)
        self.assertEqual(self.env_wrapper.min_tick, 34)
        self.assertEqual(self.env_wrapper.interval, timedelta(days=1))
        self.assertEqual(self.env_wrapper.interval_in_ticks, 24)
        self.assertEqual(self.env_wrapper.test_mode, False)
        self.assertEqual(self.env_wrapper.test_data_start_tick, self.data_start_tick)

    def test_set_to_test(self):
        self.env_wrapper.set_to_test_and_reset()
        self.assertTrue(self.env_wrapper.test_mode)
        self.assertEqual(self.env._start_tick, self.data_start_tick)
        self.assertEqual(
            self.env._start_datetime.replace(minute=0),
            self.env_wrapper.start_datetime + timedelta(hours=self.data_start_tick)
        )

    def test_interval_ticks_generator(self):
        ticks = [next(self.env_wrapper._ep_interval_ticks_generator) for _ in range(100)]
        # check if ticks are within allowed range
        self.assertTrue(all([self.env_wrapper.min_tick <= t <= self.env_wrapper.test_data_start_tick
                             for t in ticks]))
        # check if ticks are of fixed values
        ticks_expected_count = (self.env_wrapper.test_data_start_tick - self.env_wrapper.min_tick) // self.env_wrapper.interval_in_ticks
        self.assertTrue(len(Counter(ticks)), ticks_expected_count)

    def test_ep_interval_from_start_tick(self):
        tick = 42
        start, end = self.env_wrapper._ep_interval_from_start_tick(tick)
        self.assertEqual(start, START_TIME + timedelta(hours=42))
        self.assertEqual(end, start + self.env_wrapper.interval)

    def test_reset(self):
        self.env_wrapper.test_mode = True
        start, end, tick = (
            self.env._start_datetime,
            self.env._end_datetime,
            self.env._start_tick,
        )
        self.env_wrapper.reset()
        new_start, new_end, new_tick = (
            self.env._start_datetime,
            self.env._end_datetime,
            self.env._start_tick,
        )
        self.assertListEqual([start, end, tick], [new_start, new_end, new_tick])

        self.env_wrapper.test_mode = False
        self.env_wrapper.reset()
        new_start, new_end, new_tick = (
            self.env._start_datetime,
            self.env._end_datetime,
            self.env._start_tick,
        )
        self.assertNotEqual(start, new_start)
        self.assertNotEqual(end, new_end)
        self.assertNotEqual(tick, new_tick)


if __name__ == '__main__':
    unittest.main()
