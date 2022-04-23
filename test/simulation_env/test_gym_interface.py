import unittest

from stable_baselines3 import A2C

from src.simulation_env import SimulationEnv
from utils import setup_default_dfs_and_callbacks


class TestSimulationEnv(unittest.TestCase):
    def test_gym_interface_works(self):
        env = SimulationEnv(setup_default_dfs_and_callbacks(), start_tick=24)

        model = A2C('MlpPolicy', env, verbose=1)
        model.learn(total_timesteps=3)

        obs = env.reset()
        for _ in range(4):
            action, _states = model.predict(obs)
            obs, rewards, dones, info = env.step(action)

    def test_step_passes_action_to_prosumer(self):
        env = SimulationEnv(setup_default_dfs_and_callbacks(), start_tick=24)
        env.step(env.action_space.sample())
        self.assertIsNotNone(env.prosumer.scheduled_buy_amounts)
        self.assertIsNotNone(env.prosumer.scheduled_sell_amounts)
        self.assertIsNotNone(env.prosumer.scheduled_buy_thresholds)
        self.assertIsNotNone(env.prosumer.scheduled_sell_thresholds)
        self.assertEqual(env.prosumer.next_day_actions, None)


if __name__ == '__main__':
    unittest.main()
