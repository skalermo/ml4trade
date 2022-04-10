import unittest

from stable_baselines3 import A2C
import numpy as np

from src.simulation_env import SimulationEnv
from utils import setup_default_dfs_and_callbacks


class TestSimulationEnv(unittest.TestCase):
    def test_gym_interface_works(self):
        env = SimulationEnv(setup_default_dfs_and_callbacks())

        model = A2C('MlpPolicy', env, verbose=1)
        # model.learn(total_timesteps=3)

        obs = env.reset()
        for _ in range(4):
            action, _states = model.predict(obs)
            obs, rewards, dones, info = env.step(action)

    def test_step_passes_action_to_prosumer(self):
        env = SimulationEnv(setup_default_dfs_and_callbacks())
        action = env.action_space.sample()
        env.step(action)
        self.assertTrue(np.array_equal(env.prosumer.scheduled_trading_amounts, action[0:48]))
        self.assertTrue(np.array_equal(env.prosumer.scheduled_price_thresholds, action[48:]))
        self.assertEqual(env.prosumer.next_day_actions, None)


if __name__ == '__main__':
    unittest.main()
