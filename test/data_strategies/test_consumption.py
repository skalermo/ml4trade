import datetime
import unittest

from ml4trade.units import MW
from ml4trade.clock import SimulationClock
from utils import setup_default_consumption_system


class TestConsumption(unittest.TestCase):
    def test_consumption(self):
        consumption_system = setup_default_consumption_system()
        power_sum = MW(0)
        for i in range(10):
            power = consumption_system.calculate_power()
            power_sum += power
        mean = power_sum.value / 10
        self.assertAlmostEqual(mean, 0.00025, 1)

    def test_consumption_per_day(self):
        clock = SimulationClock(datetime.datetime(2020, 1, 1, hour=0))
        consumption_system = setup_default_consumption_system(clock)
        power_sum = MW(0)
        for j in range(10):
            daily_sum = MW(0)
            for i in range(24):
                power = consumption_system.calculate_power()
                daily_sum += power
                clock.tick()
            power_sum += daily_sum
        mean = power_sum.value / 10
        self.assertAlmostEqual(mean, 0.00538, 1)

    def test_data_length(self):
        consumption_system = setup_default_consumption_system(window_size=26)
        data_length = len(consumption_system.ds.energy_consumption_MWh)
        self.assertEqual(data_length, 48)


if __name__ == '__main__':
    unittest.main()
