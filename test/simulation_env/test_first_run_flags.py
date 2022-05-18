import unittest
from datetime import timedelta, datetime

from ml4trade.simulation_env import SimulationEnv
from ml4trade.constants import SCHEDULING_TIME
from utils import setup_default_data_strategies


class TestSimulationEnv(unittest.TestCase):
    def test_no_setting_actions_before_first_step(self):
        env = SimulationEnv(
            data_strategies=setup_default_data_strategies(),
            start_datetime=datetime.combine(datetime.today(), SCHEDULING_TIME) + timedelta(hours=1)
        )
        env._run_in_random_order = lambda *args: None

        self.assertFalse(env._first_actions_set)
        env.step(env.action_space.sample())
        self.assertTrue(env._first_actions_set)


if __name__ == '__main__':
    unittest.main()
