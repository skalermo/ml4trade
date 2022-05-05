from typing import List

import pandas as pd

from src.data_strategies import DataStrategy
from src.units import kW


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


def _preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.iloc[:, list(imgw_col_ids.values())]
    df.columns = list(imgw_col_ids.keys())
    return df


class ImgwWindDataStrategy(DataStrategy):
    col = 'wind_speed'
    col_idx = list(imgw_col_ids.keys()).index(col)

    def process(self, idx: int) -> kW:
        # wind speed in meters per second
        wind_speed = self.df.iat[idx, self.col_idx]
        if wind_speed > MAX_WIND_SPEED or wind_speed < 0:
            return kW(0)
        power = kW(wind_speed * MAX_WIND_POWER.value / MAX_WIND_SPEED)
        return power

    def observation(self, idx: int) -> List[float]:
        return self.df.iloc[idx - self._window_size + 1:idx + 1, self.col_idx]


class ImgwSolarDataStrategy(DataStrategy):
    col = 'cloudiness'

    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        return _preprocess_data(df)

    def process(self, idx: int) -> kW:
        # cloudiness in oktas
        # https://en.wikipedia.org/wiki/Okta 
        cloudiness = self.df.loc[idx, self.col]
        if cloudiness == 9:     # 9 equals lack of observation (sky obscured)
            cloudiness = 8      # 8 equals overcast
        power = kW(MAX_SOLAR_POWER.value * (1 - cloudiness / 8))
        return power

    def observation(self, idx: int) -> List[float]:
        return self.df.loc[idx - self._window_size + 1:idx, self.col]
