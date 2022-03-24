import datetime
import unittest

from src.custom_types import kW
from src.energy_manipulation.consumption import ConsumptionSystem


class TestConsumption(unittest.TestCase):
    def test_consumption(self):
        consumption_system = ConsumptionSystem()
        power_sum = kW(0)
        for i in range(100):
            power = consumption_system.get_power(datetime.date)
            power_sum += power
        mean = power_sum.value / 100
        self.assertAlmostEqual(mean, 5.47, 1)


if __name__ == '__main__':
    unittest.main()
