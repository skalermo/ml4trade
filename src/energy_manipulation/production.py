from datetime import datetime
import pandas

from pandas import DataFrame
from src.custom_types import kW

ENERGY_PRODUCTION_PATH = './data/.data/weather_unzipped_flattened/s_t_02_2022.csv'
MAX_WIND_POWER = kW(10)
MAX_WIND_SPEED = 11
WIND_TURBINE_EFFICIENCY = 0.15
MAX_SOLAR_POWER = kW(1)
SOLAR_EFFICIENCY = 0.2

col_ids = {'code': 0,
           'year': 2,
           'month': 3,
           'day': 4,
           'hour': 5,
           'cloudiness': 21,
           'wind_speed': 25,
           'temperature': 29}


class ProductionSystem:
    def __init__(self, df: DataFrame):
        self.df = df

    def calculate_power(self, _datetime: datetime) -> kW:
        df = self.df
        df = df.loc[df['code'] == 349190600]
        df = df.loc[df['year'] == 2022]
        df = df.loc[df['month'] == 2]
        day = int(_datetime.strftime("%Y%m%d%H%M%S")[6:8])
        df = df.loc[df['day'] == day]
        hour = int(_datetime.strftime("%Y%m%d%H%M%S")[8:10])
        df = df.loc[df['hour'] == hour]
        return self._calculate_power(_datetime, df)

    @staticmethod
    def _calculate_power(_datetime: datetime, df: DataFrame):
        return kW(5)


class WindSystem(ProductionSystem):
    def _calculate_power(self, _datetime: datetime, df: DataFrame):
        power = kW(0)
        wind_speed = df.iloc[0, 6]
        if wind_speed > MAX_WIND_SPEED or wind_speed < 0:
            return power
        power = kW(wind_speed * MAX_WIND_POWER.value / MAX_WIND_SPEED)
        return power


class SolarSystem(ProductionSystem):
    def _calculate_power(self, _datetime: datetime, df: DataFrame):
        cloudiness = df.iloc[0, 5]
        if cloudiness == 9:     # 9 equals lack of observation (sky obscured)
            cloudiness = 8      # 8 equals overcast
        power = kW(MAX_SOLAR_POWER.value * (1 - cloudiness / 8))
        return power
