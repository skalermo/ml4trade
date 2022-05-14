import unittest
from src.battery import Battery
from src.production import ProductionSystem
from src.units import MW, MWh, Currency
from src.prosumer import Prosumer
from src.clock import SimulationClock

from utils import setup_default_market, setup_default_consumption_system


class TestProduceConsumeEnergy(unittest.TestCase):
    def setUp(self):
        battery = Battery(MWh(0.1), 1.0, MWh(0.05))
        energy_market = setup_default_market()
        self.production = ProductionSystem(None, None)
        self.consumption = setup_default_consumption_system()
        self.prosumer = Prosumer(battery, self.production, self.consumption, SimulationClock().view(), Currency(50), energy_market)

    def test_consume_energy(self):
        self.consumption.calculate_power = lambda: MW(0.01)

        self.prosumer._consume_energy()

        self.assertEqual(self.prosumer.energy_balance.value, MWh(-0.01))

    def test_produce_energy(self):
        self.production.calculate_power = lambda: MW(0.01)

        self.prosumer._produce_energy()

        self.assertEqual(self.prosumer.energy_balance.value, MWh(0.01))


if __name__ == '__main__':
    unittest.main()
