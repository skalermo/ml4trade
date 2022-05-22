import unittest
import os
import datetime

import pandas as pd

from ml4trade.production import ProductionSystem
from ml4trade.units import MWh
from ml4trade.clock import SimulationClock
from ml4trade.data_strategies import ImgwWindDataStrategy, ImgwSolarDataStrategy, imgw_col_ids


weather_data_path = os.path.join(os.path.dirname(__file__), '../mock_data/s_t_02-03_2022.csv')


class TestProduction(unittest.TestCase):
    def setUp(self):
        self.df = pd.read_csv(weather_data_path, header=None, encoding='cp1250', usecols=imgw_col_ids.values())

        self.clock = SimulationClock(datetime.datetime(2020, 1, 1, hour=0))

    def test_wind_production(self):
        wind_production_system = ProductionSystem(ImgwWindDataStrategy(self.df), self.clock.view())
        energy = wind_production_system.calculate_energy()
        calculated_energy = MWh(0.002 * 10 / 11)
        self.assertEqual(energy, calculated_energy)

    def test_solar_production(self):
        solar_production_system = ProductionSystem(ImgwSolarDataStrategy(self.df), self.clock.view())
        energy = solar_production_system.calculate_energy()
        calculated_energy = MWh(0.001)
        self.assertEqual(energy, calculated_energy)


if __name__ == '__main__':
    unittest.main()
