import unittest

from ml4trade.simulation_env import SimulationEnv
from ml4trade.domain.units import MWh, Currency
from ml4trade.domain.constants import START_TIME, SCHEDULING_TIME, ACTION_REPLACEMENT_TIME
from utils import setup_default_data_strategies


class TestSetupSystems(unittest.TestCase):
    def test_setup_systems(self):
        _, prosumer, *_ = SimulationEnv._setup_systems(
            setup_default_data_strategies(), 0, Currency(1),
            START_TIME, SCHEDULING_TIME, ACTION_REPLACEMENT_TIME,
            MWh(0.001), 0.1, MWh(0.001))
        self.assertEqual(prosumer.production_system.calculate_energy(), MWh(0.0002))
        self.assertEqual(prosumer.wallet.balance, Currency(1))
        self.assertEqual(prosumer.battery.current_charge, MWh(0.001))
        self.assertEqual(prosumer.battery.capacity, MWh(0.001))
        self.assertEqual(prosumer.battery.efficiency, 0.1)


if __name__ == '__main__':
    unittest.main()
