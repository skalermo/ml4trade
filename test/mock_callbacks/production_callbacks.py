from typing import List

from pandas import DataFrame

from src.callback import Callback
from src.custom_types import kW


MAX_WIND_POWER = kW(10)
MAX_WIND_SPEED = 11

MAX_SOLAR_POWER = kW(1)
SOLAR_EFFICIENCY = 0.2

# "349190600", "BIELSKO-BIA�A", "2022", "02", "01", "00", "4", "", 320, "", 0, "8", "", "", "", 6, "", 4082, "", 4082, "", 0, "8", 264, "", 2, "", 0, "9", -.7, "", .0, "8", "U", "", 5.5, "", 95, "", -1.4, "", 959.4, "", 1008.7, "", 1, 1.8, "", .0, "", 0, "8", "85", "", "", "", "", "8", "", "", "8", "", "", "8", "", 0, "8", .3, "", .0, "8", "", "8", 0, "9", "", "", -.2, "", .1, "", .7, "", 1.8, "", 3.9, "", .0, "8", .0, "8", .0, "8", .0, "8", 0, "8", 0, "8", 0, "8", "", "", 0, "8", 0, "8"
imgw_col_ids = {
    'code': 0,
    'year': 2,
    'month': 3,
    'day': 4,
    'hour': 5,
    'cloudiness': 21,
    'wind_speed': 25,
    'temperature': 29
}


class ImgwWindCallback(Callback):
    def preprocess_data(self, df: DataFrame) -> None:
        pass

    def processed_columns(self) -> List[str]:
        return ['code', 'year', 'month', 'day', 'hour', 'wind_speed']

    def process(self, df: DataFrame, idx: int) -> kW:
        # wind speed in meters per second
        wind_speed = df.loc[idx, 'wind_speed']
        if wind_speed > MAX_WIND_SPEED or wind_speed < 0:
            return kW(0)
        power = kW(wind_speed * MAX_WIND_POWER.value / MAX_WIND_SPEED)
        return power

    def observation(self, df: DataFrame, idx: int) -> List[float]:
        return [df.loc[idx, 'wind_speed']]


class ImgwSolarCallback(Callback):
    def preprocess_data(self, df: DataFrame) -> None:
        pass

    def processed_columns(self) -> List[str]:
        return ['code', 'year', 'month', 'day', 'hour', 'cloudiness']

    def process(self, df: DataFrame, idx: int) -> kW:
        # cloudiness in oktas
        # https://en.wikipedia.org/wiki/Okta 
        cloudiness = df.loc[idx, 'cloudiness']
        if cloudiness == 9:     # 9 equals lack of observation (sky obscured)
            cloudiness = 8      # 8 equals overcast
        power = kW(MAX_SOLAR_POWER.value * (1 - cloudiness / 8))
        return power

    def observation(self, df: DataFrame, idx: int) -> List[float]:
        return [df.loc[idx, 'cloudiness']]
