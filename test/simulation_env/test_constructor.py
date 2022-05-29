import unittest
import os
from datetime import datetime

import numpy as np
import pandas as pd

from ml4trade.simulation_env import SimulationEnv
from utils import setup_default_data_strategies


class TestSimulationEnv(unittest.TestCase):
    def setUp(self) -> None:
        self.env = SimulationEnv(setup_default_data_strategies())

    def test_action_space(self):
        self.assertEqual(self.env.action_space.shape, (96,))
        amount = self.env.action_space.sample()[0]
        threshold = self.env.action_space.sample()[48]
        self.assertTrue(0 <= amount < np.inf)
        self.assertTrue(0 <= threshold < np.inf)

    def test_first_run_flags(self):
        self.assertFalse(self.env._first_actions_scheduled)
        self.assertFalse(self.env._first_actions_set)

    def test_start_datetime_matches_df_time(self):
        env = SimulationEnv(setup_default_data_strategies(),
                            start_datetime=datetime(year=2016, month=1, day=1),
                            end_datetime=datetime(year=2016, month=1, day=15))
        prices_pl_path = os.path.join(os.path.dirname(__file__), '../mock_data/prices_pl.csv')
        prices_df = pd.read_csv(prices_pl_path, header=0)
        expected_start_datetime = datetime.fromisoformat(prices_df.iloc[env._start_tick, 0])
        self.assertEqual(env._start_tick, 24 + 10)
        self.assertEqual(env._start_datetime, expected_start_datetime)

    def test_custom_start_tick(self):
        env = SimulationEnv(setup_default_data_strategies(),
                            start_datetime=datetime(year=2016, month=1, day=1),
                            end_datetime=datetime(year=2016, month=1, day=15),
                            start_tick=3)
        prices_pl_path = os.path.join(os.path.dirname(__file__), '../mock_data/prices_pl.csv')
        prices_df = pd.read_csv(prices_pl_path, header=0)
        expected_start_datetime = datetime.fromisoformat(prices_df.iloc[env._start_tick, 0])
        self.assertEqual(env._start_tick, 3)
        self.assertEqual(env._start_datetime, expected_start_datetime)


if __name__ == '__main__':
    unittest.main()
