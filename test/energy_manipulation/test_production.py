import datetime
import unittest
import os

import pandas as pd

from src.energy_manipulation.production import WindSystem
from src.energy_manipulation.production import col_ids


class TestProduction(unittest.TestCase):
    def test_wind_production(self):
        weather_data_path = os.path.join(os.path.dirname(__file__), '../mock_data/s_t_02_2022.csv')
        df = pd.read_csv(weather_data_path, header=None, names=col_ids.keys(), usecols=col_ids.values(),
                         encoding='cp1250')

        wind_production_system = WindSystem(df)
        _datetime = datetime.datetime(2022, 2, 2, 10)
        power = wind_production_system.calculate_power(_datetime)
        calculated_power = 8*10/11
        self.assertEqual(power.value, calculated_power)


if __name__ == '__main__':
    unittest.main()
