import unittest
from datetime import timedelta

from ml4trade.simulation_env import SimulationEnv
from ml4trade.constants import START_TIME
from utils import setup_default_data_strategies


class TestSimulationEnv(unittest.TestCase):
    def test_prev_step_returns_on_scheduling_time(self):
        start_datetime = START_TIME
        scheduling_time = (start_datetime + timedelta(hours=10)).time()
        env = SimulationEnv(setup_default_data_strategies(), start_datetime=start_datetime, scheduling_time=scheduling_time)
        env._run_in_random_order = lambda *args: None
        env.step(env.action_space.sample())
        self.assertTrue(env._clock.is_it_scheduling_hour())

    def test_24_hours_pass_between_consecutive_steps(self):
        env = SimulationEnv(setup_default_data_strategies())
        env._run_in_random_order = lambda *args: None
        clock = env._clock
        datetime_before = clock.cur_datetime
        env.step(env.action_space.sample())
        self.assertEqual(clock.cur_datetime, datetime_before + timedelta(days=1))
        env.step(env.action_space.sample())
        self.assertEqual(clock.cur_datetime, datetime_before + timedelta(days=2))

    def test_time_flows_independently_in_envs(self):
        start_datetime = START_TIME
        env1 = SimulationEnv(setup_default_data_strategies(), start_datetime=start_datetime)
        env2 = SimulationEnv(setup_default_data_strategies(), start_datetime=start_datetime)
        env1._run_in_random_order = lambda *args: None
        env1.step(env1.action_space.sample())
        self.assertNotEqual(env1._clock.cur_datetime, env2._clock.cur_datetime)


if __name__ == '__main__':
    unittest.main()

