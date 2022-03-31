from datetime import datetime
from typing import Callable
import pandas

from pandas import DataFrame
from src.custom_types import kW

ENERGY_PRODUCTION_PATH = './data/.data/weather_unzipped_flattened/s_t_02_2022.csv'
MAX_WIND_POWER = kW(10)
MAX_WIND_SPEED = 11
WIND_TURBINE_EFFICIENCY = 0.15
MAX_SOLAR_POWER = kW(500)
SOLAR_EFFICIENCY = 0.2


def _default_callback(_datetime: datetime):
    return kW(5)


class ProductionSystem:
    def get_power(self, _datetime: datetime, callback: Callable = _default_callback) -> kW:
        df = pandas.read_csv(ENERGY_PRODUCTION_PATH, header=None, names=['code', 'year', 'month', 'day', 'hour',
                                                                         'cloudiness', 'wind_speed', 'temperature'],
                             usecols=[0, 2, 3, 4, 5, 21, 25, 29])
        df = df.loc[lambda t: t['code'] == 349190600]
        df = df.loc([lambda t: t['year'] == datetime.year])
        df = df.loc([lambda t: t['month'] == 2])
        df = df.loc([lambda t: t['day'] == datetime.day])
        df = df.loc([lambda t: t['hour'] == datetime.hour])
        temperature = df.iloc[0, 7]
        if temperature > -30 or temperature > 40:
            return kW(0)
        return callback(_datetime, df)


class WindSystem (ProductionSystem):
    def _default_callback(self, _datetime: datetime, df: DataFrame):
        power = kW(0)
        wind_speed = df.iloc[0, 6]
        if wind_speed > MAX_WIND_SPEED or wind_speed < 0:
            return power
        power = kW(wind_speed*MAX_WIND_POWER.value*WIND_TURBINE_EFFICIENCY/MAX_WIND_SPEED)
        return power


class SolarSystem (ProductionSystem):
    def _default_callback(self, _datetime: datetime, df: DataFrame):
        cloudiness = df.iloc[0, 5]
        if cloudiness == 9:
            cloudiness = 8
        power = kW(MAX_SOLAR_POWER.value*SOLAR_EFFICIENCY*(1-cloudiness/8))
        return power
