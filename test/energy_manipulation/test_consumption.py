import datetime
import unittest

from src.custom_types import kW
from src.energy_manipulation.consumption import ConsumptionSystem
from src.clock import SimulationClock


class TestConsumption(unittest.TestCase):
    def test_consumption(self):
        clock = SimulationClock(datetime.datetime(2020, 1, 1, hour=12))
        consumption_system = ConsumptionSystem(clock.view())
        power_sum = kW(0)
        for i in range(10):
            power = consumption_system.calculate_power()
            power_sum += power
        mean = power_sum.value / 10
        self.assertAlmostEqual(mean, 0.25, 1)

    def test_consumption_per_day(self):
        clock = SimulationClock(datetime.datetime(2020, 1, 1, hour=0))
        consumption_system = ConsumptionSystem(clock.view())
        power_sum = kW(0)
        for j in range(10):
            daily_sum = kW(0)
            for i in range(24):
                power = consumption_system.calculate_power()
                daily_sum += power
                clock.tick()
            power_sum += daily_sum
        mean = power_sum.value / 10
        self.assertAlmostEqual(mean, 5.38, 1)


if __name__ == '__main__':
    unittest.main()
