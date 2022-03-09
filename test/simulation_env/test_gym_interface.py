import unittest

from stable_baselines3 import A2C

from src.simulation_env import SimulationEnv


class TestSimulationEnv(unittest.TestCase):
    def test_gym_interface_works(self):
        env = SimulationEnv()

        model = A2C('MlpPolicy', env, verbose=1)
        model.learn(total_timesteps=3)

        obs = env.reset()
        for _ in range(10):
            action, _states = model.predict(obs)
            obs, rewards, dones, info = env.step(action)


if __name__ == '__main__':
    unittest.main()
