import unittest

from src.simulation_env import SimulationEnv
from src.clock import SimulationClock
from src.units import kW, kWh, Currency
from utils import setup_default_data_strategies


class TestSetupSystems(unittest.TestCase):
    def test_setup_systems(self):
        prosumer, *_ = SimulationEnv._setup_systems(
            setup_default_data_strategies(),
            SimulationClock(),
            Currency(1), kWh(1), 0.1, kWh(1),
        )
        self.assertEqual(prosumer.production_system.calculate_power(), kW(1))
        self.assertEqual(prosumer.wallet.balance, Currency(1))
        self.assertEqual(prosumer.battery.current_charge, kWh(1))
        self.assertEqual(prosumer.battery.capacity, kWh(1))
        self.assertEqual(prosumer.battery.efficiency, 0.1)


if __name__ == '__main__':
    unittest.main()
