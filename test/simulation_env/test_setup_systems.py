import unittest

from ml4trade.simulation_env import SimulationEnv
from ml4trade.clock import SimulationClock
from ml4trade.units import MW, MWh, Currency
from utils import setup_default_data_strategies


class TestSetupSystems(unittest.TestCase):
    def test_setup_systems(self):
        prosumer, *_ = SimulationEnv._setup_systems(
            setup_default_data_strategies(),
            SimulationClock(),
            Currency(1), MWh(0.001), 0.1, MWh(0.001),
        )
        self.assertEqual(prosumer.production_system.calculate_power(), MW(0.001))
        self.assertEqual(prosumer.wallet.balance, Currency(1))
        self.assertEqual(prosumer.battery.current_charge, MWh(0.001))
        self.assertEqual(prosumer.battery.capacity, MWh(0.001))
        self.assertEqual(prosumer.battery.efficiency, 0.1)


if __name__ == '__main__':
    unittest.main()
