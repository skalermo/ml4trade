import unittest
from datetime import datetime, timedelta, time

from src.simulation_env import SimulationEnv
from utils import time_travel


class TestSimulationEnv(unittest.TestCase):
    def test_is_now_scheduling_time(self):
        scheduling_time = time(hour=12, minute=30)
        env = SimulationEnv(scheduling_time=scheduling_time)

        self.assertTrue(env.is_now_scheduling_time())
        time_travel(env, timedelta(hours=1))
        self.assertFalse(env.is_now_scheduling_time())
        time_travel(env, timedelta(hours=23))
        self.assertTrue(env.is_now_scheduling_time())

    def test_is_now_action_replacement_time(self):
        env = SimulationEnv()
        env.action_replacement_time = env.cur_datetime + timedelta(hours=1)

        self.assertFalse(env.is_now_action_replacement_time())
        time_travel(env, timedelta(hours=1))
        self.assertTrue(env.is_now_action_replacement_time())
        time_travel(env, timedelta(hours=1))
        self.assertFalse(env.is_now_action_replacement_time())

    def test_prev_step_returns_on_scheduling_time(self):
        start_datetime = datetime(2022, 1, 1)
        scheduling_time = (start_datetime + timedelta(hours=10)).time()
        env = SimulationEnv(start_datetime=start_datetime, scheduling_time=scheduling_time)
        env.step(env.action_space.sample())

        self.assertTrue(env.is_now_scheduling_time())

    def test_24_hours_pass_between_consecutive_steps(self):
        start_datetime = datetime(2022, 1, 1)
        env = SimulationEnv(start_datetime=start_datetime)

        env_time = env.cur_datetime
        env.step(env.action_space.sample())
        self.assertEqual(env.cur_datetime, env_time + timedelta(days=1))
        env.step(env.action_space.sample())
        self.assertEqual(env.cur_datetime, env_time + timedelta(days=2))


if __name__ == '__main__':
    unittest.main()

