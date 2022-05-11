import unittest

from src.battery import Battery
from src.production import ProductionSystem
from src.units import MWh, Currency
from src.prosumer import Prosumer
from utils import setup_default_market, setup_default_consumption_system


class TestProsumer(unittest.TestCase):
    def test_init(self):
        battery = Battery(MWh(0.1), 1.0, MWh(0.05))
        production_system = ProductionSystem(None, None)
        consumption_system = setup_default_consumption_system()
        energy_market = setup_default_market()
        prosumer = Prosumer(battery, production_system, consumption_system, Currency(50), energy_market)
        self.assertEqual(prosumer.battery.capacity, MWh(0.1))


if __name__ == '__main__':
    unittest.main()
