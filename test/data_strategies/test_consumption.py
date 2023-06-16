import unittest

from ml4trade.data_strategies.consumption import HouseholdEnergyConsumptionDataStrategy
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
        self.assertAlmostEqual(mean, 0.00025, 2)

    def test_consumption_per_day(self):
        clock = setup_default_clock()
        consumption_system = setup_default_consumption_system(clock, household_number=42)
        energy_sum = MWh(0)
        for j in range(10):
            daily_sum = MWh(0)
            for i in range(24):
                energy = consumption_system.calculate_energy()
                daily_sum += energy
                clock.tick()
            energy_sum += daily_sum
        mean = energy_sum.value / 10
        self.assertAlmostEqual(mean, 0.00538 * 42, 2)

    def test_data_length(self):
        consumption_system = setup_default_consumption_system(window_size=26)
        data_length = len(consumption_system.ds.energy_consumption_MWh)
        self.assertEqual(data_length, 48)


class TestDs(unittest.TestCase):
    def test_hour_consumption(self):
        household_number = 42
        hour = 13
        ds = setup_default_consumption_system(household_number=household_number).ds
        v = ds.calculate_power_value(hour=hour, household_number=household_number, noise=0)
        self.assertEqual(v, HouseholdEnergyConsumptionDataStrategy.energy_consumption_MWh[hour] * household_number)

    def test_observation(self):
        household_number = 42
        window_size = 69
        clock = setup_default_clock()
        consumption_system = setup_default_consumption_system(clock, household_number=household_number, window_size=window_size)
        obs = consumption_system.observation()
        start = clock.cur_datetime.hour - 10
        end = start + window_size
        values = list(map(lambda x: x * household_number, HouseholdEnergyConsumptionDataStrategy.energy_consumption_MWh[start:end]))
        self.assertEqual(obs, values)


if __name__ == '__main__':
    unittest.main()
