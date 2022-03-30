import datetime
import unittest

from src.custom_types import kW
from src.energy_manipulation.consumption import ConsumptionSystem


class TestConsumption(unittest.TestCase):
    def test_consumption(self):
        consumption_system = ConsumptionSystem()
        power_sum = kW(0)
        for i in range(100):
            power = consumption_system.get_power(datetime.time(12))
            power_sum += power
        mean = power_sum.value / 100
        self.assertAlmostEqual(mean, 0.24, 1)

    def test_consumption_per_day(self):
        consumption_system = ConsumptionSystem()
        power_sum = kW(0)
        for i in range(24):
            power = consumption_system.get_power(datetime.time(i))
            power_sum += power
        self.assertAlmostEqual(power_sum.value, 5.38, 1)


if __name__ == '__main__':
    unittest.main()
