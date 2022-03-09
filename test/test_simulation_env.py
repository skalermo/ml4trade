import unittest
from datetime import datetime, timedelta, time

from stable_baselines3 import A2C

from src.simulation_env import SimulationEnv
from utils import time_travel


class TestSimulationEnv(unittest.TestCase):
    def test_gym_interface_works(self):
        env = SimulationEnv()

        model = A2C('MlpPolicy', env, verbose=1)
        model.learn(total_timesteps=3)

        obs = env.reset()
        for _ in range(10):
            action, _states = model.predict(obs)
            obs, rewards, dones, info = env.step(action)

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


if __name__ == '__main__':
    unittest.main()
