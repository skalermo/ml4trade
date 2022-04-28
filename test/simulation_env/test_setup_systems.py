import unittest

from src.simulation_env import SimulationEnv
from src.clock import SimulationClock
from src.custom_types import kW
from utils import setup_default_data_strategies


class TestSetupSystems(unittest.TestCase):
    def test_setup_systems(self):
        prosumer, *_ = SimulationEnv._setup_systems(setup_default_data_strategies(), SimulationClock())
        self.assertEqual(prosumer.production_system.calculate_power(), kW(1))


if __name__ == '__main__':
    unittest.main()
