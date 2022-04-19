import unittest
from src.battery import Battery
from src.energy_manipulation.energy_systems import EnergySystems
from src.custom_types import kW, kWh, Currency
from src.prosumer import Prosumer
from src.clock import SimulationClock

from utils import setup_default_market


class TestProduceConsumeEnergy(unittest.TestCase):
    def setUp(self):
        battery = Battery(kWh(100), 1.0, kWh(50))
        energy_market = setup_default_market()
        self.energy_systems = EnergySystems()
        self.prosumer = Prosumer(battery, self.energy_systems, SimulationClock().view(), Currency(50), energy_market)

    def test_consume_energy(self):
        self.energy_systems.get_consumption_power = lambda x: kW(10)

        self.prosumer._consume_energy()

        self.assertEqual(self.prosumer.energy_balance.value, kWh(-10))

    def test_produce_energy(self):
        self.energy_systems.get_production_power = lambda x: kW(10)

        self.prosumer._produce_energy()

        self.assertEqual(self.prosumer.energy_balance.value, kWh(10))


if __name__ == '__main__':
    unittest.main()
