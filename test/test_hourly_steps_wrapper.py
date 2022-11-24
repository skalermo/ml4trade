import unittest
from datetime import timedelta

from ml4trade.domain.units import MWh
from ml4trade.domain.constants import START_TIME
from ml4trade.misc.hourly_steps_wrapper import HourlyStepsWrapper
from utils import setup_default_simulation_env


class TestHourlyStepsWrapper(unittest.TestCase):
    def setUp(self) -> None:
        self.end_datetime = START_TIME + timedelta(days=14)
        self.battery_init_charge = MWh(0.42)
        self.env = HourlyStepsWrapper(setup_default_simulation_env(
            end_datetime=self.end_datetime,
            battery_init_charge=self.battery_init_charge
        ))

    def test_run(self):
        obs = self.env.reset()
        for i in range(48):
            action = self.env.action_space.sample()
            print(i, action, obs)
            obs = self.env.step(action)


if __name__ == '__main__':
    unittest.main()
