import unittest
from datetime import datetime, timedelta, time

import numpy as np

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

    def test_start_datetime(self):
        start_datetime = datetime(2022, 1, 1)
        env = SimulationEnv(start_datetime=start_datetime)

        self.assertEqual(env.cur_datetime, start_datetime)

    def test_scheduling_time(self):
        scheduling_time = time(hour=12, minute=45)
        env = SimulationEnv(scheduling_time=scheduling_time)

        self.assertEqual(env.scheduling_time, scheduling_time)

    def test_action_replacement_time(self):
        action_replacement_time = time(hour=12, minute=45)
        env = SimulationEnv(scheduling_time=action_replacement_time)

        self.assertEqual(env.scheduling_time, action_replacement_time)

    def test_action_space(self):
        env = SimulationEnv()
        self.assertEqual(env.action_space.shape, (48,))
        amount = env.action_space.sample()[0]
        threshold = env.action_space.sample()[24]
        self.assertTrue(-np.inf < amount < np.inf)
        self.assertTrue(0 < threshold < np.inf)


if __name__ == '__main__':
    unittest.main()
