import unittest

import numpy as np

from src.simulation_env import SimulationEnv
from utils import setup_default_data_strategies


class TestSimulationEnv(unittest.TestCase):
    def setUp(self) -> None:
        self.env = SimulationEnv(setup_default_data_strategies(), start_tick=24)

    def test_action_space(self):
        self.assertEqual(self.env.action_space.shape, (96,))
        amount = self.env.action_space.sample()[0]
        threshold = self.env.action_space.sample()[48]
        self.assertTrue(0 <= amount < np.inf)
        self.assertTrue(0 <= threshold < np.inf)

    def test_first_run_flags(self):
        self.assertFalse(self.env.first_actions_scheduled)
        self.assertFalse(self.env.first_actions_set)


if __name__ == '__main__':
    unittest.main()
