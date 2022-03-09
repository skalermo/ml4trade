import unittest
from datetime import datetime, timedelta

from src.simulation_env import SimulationEnv
from utils import time_travel


class TestSimulationEnv(unittest.TestCase):
    def test_is_now_scheduling_time(self):
        start_datetime = datetime(2022, 1, 1)
        scheduling_time = (start_datetime + timedelta(hours=1)).time()
        env = SimulationEnv(start_datetime=start_datetime, scheduling_time=scheduling_time)

        self.assertFalse(env.is_now_scheduling_time())
        time_travel(env, timedelta(hours=1))
        self.assertTrue(env.is_now_scheduling_time())
        time_travel(env, timedelta(hours=1))
        self.assertFalse(env.is_now_scheduling_time())

    def test_is_now_action_replacement_time(self):
        start_datetime = datetime(2022, 1, 1)
        action_replacement_time = (start_datetime + timedelta(hours=1)).time()
        env = SimulationEnv(start_datetime=start_datetime, action_replacement_time=action_replacement_time)

        self.assertFalse(env.is_now_action_replacement_time())
        time_travel(env, timedelta(hours=1))
        self.assertTrue(env.is_now_action_replacement_time())
        time_travel(env, timedelta(hours=1))
        self.assertFalse(env.is_now_action_replacement_time())

    def test_prev_step_returns_on_scheduling_time(self):
        start_datetime = datetime(2022, 1, 1)
        scheduling_time = (start_datetime + timedelta(hours=10)).time()
        env = SimulationEnv(start_datetime=start_datetime, scheduling_time=scheduling_time)
        env.step(None)

        self.assertTrue(env.is_now_scheduling_time())

    def test_24_hours_pass_between_consecutive_steps(self):
        start_datetime = datetime(2022, 1, 1)
        env = SimulationEnv(start_datetime=start_datetime)
        env.step(None)

        env_time = env.cur_datetime
        env.step(None)
        self.assertEqual(env.cur_datetime, env_time + timedelta(days=1))
        env.step(None)
        self.assertEqual(env.cur_datetime, env_time + timedelta(days=2))


if __name__ == '__main__':
    unittest.main()

