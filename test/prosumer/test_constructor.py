import unittest

from src.battery import Battery
from src.energy_manipulation.energy_systems import EnergySystems
from src.custom_types import kWh, Currency
from src.market import EnergyMarket
from src.prosumer import Prosumer


class TestProsumer(unittest.TestCase):
    def test_init(self):
        battery = Battery(kWh(100), 1.0, kWh(50))
        energy_systems = EnergySystems()
        energy_market = EnergyMarket(Currency(0.5), Currency(1))
        prosumer = Prosumer(battery, energy_systems, Currency(50), energy_market)
        self.assertEqual(prosumer.battery.capacity, kWh(100))


if __name__ == '__main__':
    unittest.main()
