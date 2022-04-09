import unittest
from datetime import datetime, timedelta

from src.simulation_env import SimulationEnv


class TestSimulationEnv(unittest.TestCase):
    def test_prev_step_returns_on_scheduling_time(self):
        start_datetime = datetime(2022, 1, 1)
        scheduling_time = (start_datetime + timedelta(hours=10)).time()
        env = SimulationEnv(start_datetime=start_datetime, scheduling_time=scheduling_time)
        env.step(env.action_space.sample())
        self.assertTrue(env._clock.is_it_scheduling_hour())

    def test_24_hours_pass_between_consecutive_steps(self):
        start_datetime = datetime(2022, 1, 1)
        env = SimulationEnv(start_datetime=start_datetime)
        clock = env._clock
        datetime_before = clock.cur_datetime
        env.step(env.action_space.sample())
        self.assertEqual(clock.cur_datetime, datetime_before + timedelta(days=1))
        env.step(env.action_space.sample())
        self.assertEqual(clock.cur_datetime, datetime_before + timedelta(days=2))

    def test_time_flows_independently_in_envs(self):
        start_datetime = datetime(2022, 1, 1)
        env1 = SimulationEnv(start_datetime=start_datetime)
        env2 = SimulationEnv(start_datetime=start_datetime)
        env1.step(env1.action_space.sample())
        self.assertNotEqual(env1._clock.cur_datetime, env2._clock.cur_datetime)


if __name__ == '__main__':
    unittest.main()

