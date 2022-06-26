import os
import unittest

import pandas as pd

from ml4trade.data_strategies import ImgwWindDataStrategy, ImgwSolarDataStrategy, imgw_col_ids
from ml4trade.domain.production import ProductionSystem
from ml4trade.domain.units import MWh, MW

from utils import setup_default_clock

weather_data_path = os.path.join(os.path.dirname(__file__), '../mock_data/s_t_02-03_2022.csv')


class TestProduction(unittest.TestCase):
    def setUp(self):
        self.df = pd.read_csv(weather_data_path, header=None, encoding='cp1250', usecols=imgw_col_ids.values())
        self.clock = setup_default_clock()
        self.windDs = ImgwWindDataStrategy(self.df, window_size=24, max_wind_power=MW(0.01), max_wind_speed=11)
        self.solarDs = ImgwSolarDataStrategy(self.df, window_size=24, max_solar_power=MW(0.001), solar_efficiency=0.2)

    def test_wind_production(self):
        wind_production_system = ProductionSystem(self.windDs, self.clock.view())
        energy = wind_production_system.calculate_energy()
        calculated_energy = MWh(0.002 * 10 / 11)
        self.assertEqual(energy, calculated_energy)

    def test_solar_production(self):
        solar_production_system = ProductionSystem(self.solarDs, self.clock.view())
        power = solar_production_system.calculate_energy()
        calculated_power = MWh(0.0002)
        self.assertEqual(power, calculated_power)

    def test_observation_frame(self):
        ds = self.solarDs
        scheduling_hour = 10
        self.assertListEqual(self.df.iloc[24:48, ds.col_idx].tolist(), ds.observation(scheduling_hour))


if __name__ == '__main__':
    unittest.main()
