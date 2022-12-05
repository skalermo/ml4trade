import unittest
from datetime import timedelta

from ml4trade.domain.clock import ClockView
from ml4trade.domain.units import MWh
from ml4trade.domain.constants import START_TIME
from ml4trade.misc.hourly_steps_wrapper import HourlyStepsWrapper
from utils import setup_default_simulation_env


class TestHourlyStepsWrapper(unittest.TestCase):
    def setUp(self) -> None:
        self.end_datetime = START_TIME + timedelta(days=14)
        self.battery_init_charge = MWh(0.1)
        self.env = HourlyStepsWrapper(setup_default_simulation_env(
            end_datetime=self.end_datetime,
            battery_init_charge=self.battery_init_charge
        ))

    def test_reset_preserves_env_hour(self):
        env_clock_view: ClockView = self.env.new_clock_view()
        self.env.reset()
        self.env.step(self.env.action_space.sample())

        obs, _ = self.env.reset()
        wrapper_hour = obs[3]
        self.assertEqual(wrapper_hour, env_clock_view.cur_datetime().hour)

    def test_step_returns_correct_hour(self):
        env_clock_view: ClockView = self.env.new_clock_view()

        obs, _ = self.env.reset()
        wrapper_hour = obs[3]
        self.assertEqual(wrapper_hour, env_clock_view.cur_datetime().hour)

        for i in range(3 * 24):
            action = self.env.action_space.sample()
            obs, *_ = self.env.step(action)
            wrapper_hour = obs[3]
            self.assertEqual(wrapper_hour, env_clock_view.cur_datetime().hour)

        self.env.reset()
        obs, *_ = self.env.step(self.env.action_space.sample())
        wrapper_hour = obs[3]
        self.assertEqual(wrapper_hour, env_clock_view.cur_datetime().hour)


if __name__ == '__main__':
    unittest.main()
