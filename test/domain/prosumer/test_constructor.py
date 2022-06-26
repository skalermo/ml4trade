import unittest

from ml4trade.domain.battery import Battery
from ml4trade.domain.production import ProductionSystem
from ml4trade.domain.units import MWh, Currency
from ml4trade.domain.prosumer import Prosumer
from utils import setup_default_market, setup_default_consumption_system, setup_default_clock


class TestProsumer(unittest.TestCase):
    def test_init(self):
        battery = Battery(MWh(0.1), 1.0, MWh(0.05))
        production_system = ProductionSystem(None, None)
        consumption_system = setup_default_consumption_system()
        energy_market = setup_default_market()
        prosumer = Prosumer(battery, production_system, consumption_system, setup_default_clock(), Currency(50), energy_market)
        self.assertEqual(prosumer.battery.capacity, MWh(0.1))
        self.assertEqual(prosumer.wallet.balance, Currency(50))


if __name__ == '__main__':
    unittest.main()
