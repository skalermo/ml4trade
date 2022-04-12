import unittest
from src.battery import Battery
from src.energy_manipulation.energy_systems import EnergySystems
from src.custom_types import kWh, Currency
from src.prosumer import Prosumer

from utils import setup_default_market


class TestProduceConsumeEnergy(unittest.TestCase):
    def test_consume_energy(self):
        battery = Battery(kWh(100), 1.0, kWh(50))
        energy_systems = EnergySystems()
        energy_market = setup_default_market()
        prosumer = Prosumer(battery, energy_systems, Currency(50), energy_market)

        prosumer.consume_energy(kWh(10))

        self.assertEqual(prosumer.energy_balance.value, kWh(-10))

    def test_produce_energy(self):
        battery = Battery(kWh(100), 1.0, kWh(50))
        energy_systems = EnergySystems()
        energy_market = setup_default_market()
        prosumer = Prosumer(battery, energy_systems, Currency(50), energy_market)

        prosumer.produce_energy(kWh(10))

        self.assertEqual(prosumer.energy_balance.value, kWh(10))


if __name__ == '__main__':
    unittest.main()
