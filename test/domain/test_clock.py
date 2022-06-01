import unittest
from datetime import datetime, time, timedelta


from ml4trade.domain.clock import SimulationClock


class TestClock(unittest.TestCase):
    def setUp(self) -> None:
        self.start_datetime = datetime(2022, 4, 9, 12, 0, 0)
        self.scheduling_time = time(10, 30, 0)
        self.action_replacement_time = time(0, 0, 0)
        self.c = SimulationClock(self.start_datetime, self.scheduling_time, self.action_replacement_time)

    def test_constructor(self):
        self.assertEqual(self.c.cur_datetime, self.start_datetime)
        self.assertEqual(self.c.cur_tick, 0)
        self.assertEqual(self.c.tick_duration, timedelta(hours=1))
        self.assertEqual(self.c.scheduling_time, self.scheduling_time)
        self.assertEqual(self.c.action_replacement_time, self.action_replacement_time)

    def test_tick(self):
        self.c.tick()
        self.assertEqual(self.c.cur_datetime, self.start_datetime + timedelta(hours=1))
        self.assertEqual(self.c.cur_tick, 1)

    def test_is_it_scheduling_hour(self):
        self.assertFalse(self.c.is_it_scheduling_hour())
        self.c.cur_datetime = datetime(2022, 4, 9, 10, 30, 0)
        self.assertTrue(self.c.is_it_scheduling_hour())

    def test_is_it_action_replacement_hour(self):
        self.assertFalse(self.c.is_it_action_replacement_hour())
        self.c.cur_datetime = datetime(2022, 4, 9, 0, 0, 0)
        self.assertTrue(self.c.is_it_action_replacement_hour())


if __name__ == '__main__':
    unittest.main()
