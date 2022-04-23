import unittest
import os
import datetime

import pandas as pd

from src.energy_manipulation.production import ProductionSystem
from src.custom_types import kW
from src.clock import SimulationClock

from mock_callbacks.production_callbacks import ImgwWindCallback, ImgwSolarCallback, imgw_col_ids


weather_data_path = os.path.join(os.path.dirname(__file__), '../mock_data/s_t_02_2022.csv')


class TestProduction(unittest.TestCase):
    def setUp(self):
        self.df = pd.read_csv(weather_data_path, header=None,
                              names=imgw_col_ids.keys(), usecols=imgw_col_ids.values(),
                              encoding='cp1250')

        self.clock = SimulationClock(datetime.datetime(2020, 1, 1, hour=0))

    def test_wind_production(self):
        wind_production_system = ProductionSystem(self.df, ImgwWindCallback(), self.clock.view())
        power = wind_production_system.calculate_power()
        calculated_power = kW(2 * 10 / 11)
        self.assertEqual(power, calculated_power)

    def test_solar_production(self):
        solar_production_system = ProductionSystem(self.df, ImgwSolarCallback(), self.clock.view())
        power = solar_production_system.calculate_power()
        calculated_power = kW(1)
        self.assertEqual(power, calculated_power)


if __name__ == '__main__':
    unittest.main()
