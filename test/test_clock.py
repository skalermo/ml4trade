import unittest
from datetime import datetime, time, timedelta


from src.clock import Clock


class TestClock(unittest.TestCase):
    def setUp(self) -> None:
        self.start_datetime = datetime(2022, 4, 9, 12, 0, 0)
        self.c = Clock(self.start_datetime)

    def test_constructor(self):
        self.assertEqual(self.c.cur_datetime, self.start_datetime)
        self.assertEqual(self.c.cur_tick, 0)
        self.assertEqual(self.c.tick_duration, timedelta(hours=1))

    def test_tick(self):
        self.c.tick()
        self.assertEqual(self.c.cur_datetime, self.start_datetime + timedelta(hours=1))
        self.assertEqual(self.c.cur_tick, 1)

    def test_is_it_time(self):
        self.assertTrue(self.c.is_it_time(time(12, 0, 0)))
        self.assertFalse(self.c.is_it_time(time(12, 0, 1)))
        self.assertFalse(self.c.is_it_time(time(11, 59, 59)))


if __name__ == '__main__':
    unittest.main()
