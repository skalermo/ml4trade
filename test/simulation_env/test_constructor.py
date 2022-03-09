import unittest
from datetime import datetime, timedelta, time

from src.simulation_env import SimulationEnv


class TestSimulationEnv(unittest.TestCase):
    def test_constructor(self):
        start_datetime = datetime(2022, 1, 1)
        scheduling_time = (start_datetime + timedelta(hours=1)).time()
        two_thirty = time(hour=2, minute=30)
        env = SimulationEnv(
            start_datetime=start_datetime,
            scheduling_time=scheduling_time,
            action_replacement_time=two_thirty
        )

        self.assertEqual(env.cur_datetime, start_datetime)
        self.assertEqual(env.scheduling_time, scheduling_time)
        self.assertEqual(env.action_replacement_time, two_thirty)


if __name__ == '__main__':
    unittest.main()
