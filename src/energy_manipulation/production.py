from datetime import datetime
from typing import Callable
import pandas

from pandas import DataFrame
from src.custom_types import kW

ENERGY_PRODUCTION_PATH = './data/.data/weather_unzipped_flattened/s_t_02_2022.csv'
MAX_WIND_POWER = kW(10)
MAX_WIND_SPEED = 11
WIND_TURBINE_EFFICIENCY = 0.15
MAX_SOLAR_POWER = kW(1)
SOLAR_EFFICIENCY = 0.2


def _default_callback(_datetime: datetime, df: DataFrame):
    return kW(5)


class ProductionSystem:
    def get_power(self, _datetime: datetime, callback: Callable = _default_callback) -> kW:
        df = pandas.read_csv(ENERGY_PRODUCTION_PATH, header=None, names=['code', 'year', 'month', 'day', 'hour',
                                                                         'cloudiness', 'wind_speed', 'temperature'],
                             usecols=[0, 2, 3, 4, 5, 21, 25, 29], encoding='ansi')
        df = df.loc[df['code'] == 349190600]
        df = df.loc[df['year'] == 2022]
        df = df.loc[df['month'] == 2]
        day = int(_datetime.strftime("%Y%m%d%H%M%S")[6:8])
        df = df.loc[df['day'] == day]
        hour = int(_datetime.strftime("%Y%m%d%H%M%S")[8:10])
        df = df.loc[df['hour'] == hour]
        print(df)
        return callback(_datetime, df)


class WindSystem (ProductionSystem):
    def _default_callback(self, _datetime: datetime, df: DataFrame):
        power = kW(0)
        wind_speed = df.iloc[0, 6]
        if wind_speed > MAX_WIND_SPEED or wind_speed < 0:
            return power
        power = kW(wind_speed*MAX_WIND_POWER.value/MAX_WIND_SPEED)
        return power


class SolarSystem (ProductionSystem):
    def _default_callback(self, _datetime: datetime, df: DataFrame):
        cloudiness = df.iloc[0, 5]
        if cloudiness == 9:
            cloudiness = 8
        power = kW(MAX_SOLAR_POWER.value*(1-cloudiness/8))
        return power
