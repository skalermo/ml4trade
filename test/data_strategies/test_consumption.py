import unittest

from ml4trade.domain.units import MWh
from utils import setup_default_consumption_system, setup_default_clock


class TestConsumption(unittest.TestCase):
    def test_consumption(self):
        consumption_system = setup_default_consumption_system()
        energy_sum = MWh(0)
        for i in range(10):
            energy = consumption_system.calculate_energy()
            energy_sum += energy
        mean = energy_sum.value / 10
        self.assertAlmostEqual(mean, 0.025, 1)

    def test_consumption_per_day(self):
        clock = setup_default_clock()
        consumption_system = setup_default_consumption_system(clock)
        energy_sum = MWh(0)
        for j in range(10):
            daily_sum = MWh(0)
            for i in range(24):
                energy = consumption_system.calculate_energy()
                daily_sum += energy
                clock.tick()
            energy_sum += daily_sum
        mean = energy_sum.value / 10
        self.assertAlmostEqual(mean, 0.538, 1)

    def test_data_length(self):
        consumption_system = setup_default_consumption_system(window_size=26)
        data_length = len(consumption_system.ds.energy_consumption_MWh)
        self.assertEqual(data_length, 48)


if __name__ == '__main__':
    unittest.main()
