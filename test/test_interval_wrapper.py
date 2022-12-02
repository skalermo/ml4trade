import unittest
from datetime import timedelta

from ml4trade.domain.units import MWh
from ml4trade.domain.constants import START_TIME
from ml4trade.misc.interval_wrapper import IntervalWrapper
from ml4trade.utils import timedelta_to_hours
from utils import setup_default_simulation_env


class TestIntervalWrapper(unittest.TestCase):
    def setUp(self) -> None:
        self.end_datetime = START_TIME + timedelta(days=14)
        self.battery_init_charge = MWh(0.1)
        self.env = setup_default_simulation_env(
            end_datetime=self.end_datetime,
            battery_init_charge=self.battery_init_charge
        )
        self.env_wrapper = IntervalWrapper(env=self.env, interval=timedelta(days=1), split_ratio=0.75)
        data_duration = timedelta(days=14) - timedelta(hours=34)
        self.data_start_tick = self.env._start_tick + timedelta_to_hours(data_duration * 0.75)

    def test_constructor(self):
        self.assertEqual(self.env_wrapper.env, self.env)
        self.assertEqual(self.env_wrapper.start_datetime, START_TIME + timedelta(hours=34))
        self.assertEqual(self.env_wrapper.end_datetime, self.end_datetime)
        self.assertEqual(self.env_wrapper.start_tick, 34)
        self.assertEqual(self.env_wrapper.interval, timedelta(days=1))
        self.assertEqual(self.env_wrapper.interval_in_ticks, 24)
        self.assertEqual(self.env_wrapper.train_mode, True)
        self.assertEqual(self.env_wrapper.test_data_start_tick, self.data_start_tick)

    # def test_set_to_test(self):
    #     self.env_wrapper.set_to_test_and_reset()
    #     self.assertFalse(self.env_wrapper.train_mode)
    #     self.assertEqual(self.env._start_tick, self.data_start_tick)
    #     self.assertEqual(
    #         self.env._start_datetime.replace(minute=0),
    #         self.env_wrapper.start_datetime + timedelta(hours=self.data_start_tick)
    #     )

    def test_interval_ticks_generator(self):
        ticks = [next(self.env_wrapper._ep_interval_ticks_generator) for _ in range(100)]
        # check if ticks are within allowed range
        self.assertTrue(all([self.env_wrapper.start_tick <= t <= self.env_wrapper.test_data_start_tick
                             for t in ticks]))

    def test_random_start_ticks(self):
        ticks_expected_count = (self.env_wrapper.test_data_start_tick - self.env_wrapper.start_tick) // self.env_wrapper.interval_in_ticks
        ticks1 = sorted([next(self.env_wrapper._ep_interval_ticks_generator) for _ in range(ticks_expected_count)])
        ticks2 = sorted([next(self.env_wrapper._ep_interval_ticks_generator) for _ in range(ticks_expected_count)])
        self.assertNotEqual(ticks1, ticks2)

    def test_ep_interval_from_start_tick(self):
        tick = 42
        start, end = self.env_wrapper._ep_interval_from_start_tick(tick)
        self.assertEqual(start, START_TIME + timedelta(hours=42))
        self.assertEqual(end, start + self.env_wrapper.interval)

    def test_reset(self):
        self.env_wrapper.train_mode = False
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

        self.env_wrapper.train_mode = True
        self.env_wrapper.reset(seed=0)
        new_start, new_end, new_tick = (
            self.env._start_datetime,
            self.env._end_datetime,
            self.env._start_tick,
        )
        self.assertNotEqual(start, new_start)
        self.assertNotEqual(end, new_end)
        self.assertNotEqual(tick, new_tick)

    def test_setting_battery_randomly_for_each_episode(self):
        self.assertEqual(self.env._prosumer.battery.current_charge, self.battery_init_charge)
        self.env_wrapper.reset()
        self.assertEqual(self.env._prosumer.battery.current_charge, self.battery_init_charge)

        self.env_wrapper.randomly_set_battery = True
        self.env_wrapper.reset(seed=42)
        self.assertNotEqual(self.env._prosumer.battery.current_charge, self.battery_init_charge)

    def test_not_allowed_interval(self):
        with self.assertRaises(AssertionError) as e:
            self.env_wrapper.set_interval(timedelta(days=42))
        self.assertTrue('Max allowed interval is 9 days' in str(e.exception))

    def test_set_interval(self):
        self.assertEqual(self.env_wrapper.interval, timedelta(days=1))

        self.env_wrapper.set_interval(timedelta(days=9))

        self.assertEqual(self.env_wrapper.interval, timedelta(days=9))
        self.assertEqual(self.env_wrapper.interval_in_ticks, 9 * 24)
        self.env_wrapper.reset()
        self.assertEqual(self.env_wrapper.env._end_datetime - self.env_wrapper.env._start_datetime, timedelta(days=9))

    def test_reset_with_seed_deterministically(self):
        self.env_wrapper.reset(seed=42)
        datetime1 = self.env_wrapper.new_clock_view().cur_datetime()
        self.env_wrapper.reset(seed=42)
        datetime2 = self.env_wrapper.new_clock_view().cur_datetime()
        self.assertEqual(datetime1, datetime2)


if __name__ == '__main__':
    unittest.main()
