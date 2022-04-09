import unittest
from datetime import datetime, time

import numpy as np

from src.simulation_env import SimulationEnv


class TestSimulationEnv(unittest.TestCase):
    def test_action_space(self):
        env = SimulationEnv()
        self.assertEqual(env.action_space.shape, (96,))
        amount = env.action_space.sample()[0]
        threshold = env.action_space.sample()[48]
        self.assertTrue(0 <= amount < np.inf)
        self.assertTrue(0 <= threshold < np.inf)


if __name__ == '__main__':
    unittest.main()
