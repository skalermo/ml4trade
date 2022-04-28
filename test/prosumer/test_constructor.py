import unittest

from src.battery import Battery
from src.production import ProductionSystem
from src.consumption import ConsumptionSystem
from src.custom_types import kWh, Currency
from src.prosumer import Prosumer
from utils import setup_default_market, setup_default_consumption_system


class TestProsumer(unittest.TestCase):
    def test_init(self):
        battery = Battery(kWh(100), 1.0, kWh(50))
        production_system = ProductionSystem(None, None)
        consumption_system = setup_default_consumption_system()
        energy_market = setup_default_market()
        prosumer = Prosumer(battery, production_system, consumption_system, Currency(50), energy_market)
        self.assertEqual(prosumer.battery.capacity, kWh(100))


if __name__ == '__main__':
    unittest.main()
