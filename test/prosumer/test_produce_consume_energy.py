import unittest
from src.battery import Battery
from src.production import ProductionSystem
from src.consumption import ConsumptionSystem
from src.custom_types import kW, kWh, Currency
from src.prosumer import Prosumer
from src.clock import SimulationClock

from utils import setup_default_market, setup_default_consumption_system


class TestProduceConsumeEnergy(unittest.TestCase):
    def setUp(self):
        battery = Battery(kWh(100), 1.0, kWh(50))
        energy_market = setup_default_market()
        self.production = ProductionSystem(None, None)
        self.consumption = setup_default_consumption_system()
        self.prosumer = Prosumer(battery, self.production, self.consumption, SimulationClock().view(), Currency(50), energy_market)

    def test_consume_energy(self):
        self.consumption.calculate_power = lambda: kW(10)

        self.prosumer._consume_energy()

        self.assertEqual(self.prosumer.energy_balance.value, kWh(-10))

    def test_produce_energy(self):
        self.production.calculate_power = lambda: kW(10)

        self.prosumer._produce_energy()

        self.assertEqual(self.prosumer.energy_balance.value, kWh(10))


if __name__ == '__main__':
    unittest.main()
