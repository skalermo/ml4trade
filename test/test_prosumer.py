import unittest
from datetime import date

from src.battery import Battery
from src.energy_manipulation.energy_systems import EnergySystems
from src.energy_types import Ah
from src.market import EnergyMarket
from src.prosumer import Prosumer


class TestProsumer(unittest.TestCase):
    def test_init(self):
        battery = Battery(Ah(100), 1.0, Ah(50))
        energy_systems = EnergySystems()
        energy_market = EnergyMarket(0.5, 1)
        prosumer = Prosumer(battery, energy_systems, 50, energy_market, date.today())
        self.assertEqual(prosumer.battery.capacity, Ah(100))

    def test_consume_energy(self):
        battery = Battery(Ah(100), 1.0, Ah(50))
        energy_systems = EnergySystems()
        energy_market = EnergyMarket(0.5, 1)
        prosumer = Prosumer(battery, energy_systems, 50, energy_market, date.today())
        # prosumer.consume_energy(5)
        pass

    def test_sell_energy(self):
        pass

    def test_buy_energy(self):
        pass


if __name__ == '__main__':
    unittest.main()
