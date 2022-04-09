import unittest
import os

import pandas as pd

from src.simulation_env import SimulationEnv
from src.custom_types import kW
from mock_callbacks.production_callbacks import ImgwSolarCallback, imgw_col_ids


weather_data_path = os.path.join(os.path.dirname(__file__), '../mock_data/s_t_02_2022.csv')


class TestSetupSystems(unittest.TestCase):
    def test_something(self):
        df = pd.read_csv(weather_data_path, header=None,
                         names=imgw_col_ids.keys(), usecols=imgw_col_ids.values(),
                         encoding='cp1250')
        dfs_and_callbacks = {'production': [(df, ImgwSolarCallback())]}
        prosumer = SimulationEnv._setup_systems(dfs_and_callbacks, 1.0, 1.0)
        self.assertEqual(prosumer.energy_systems.get_production_power(idx=0), kW(1))


if __name__ == '__main__':
    unittest.main()
