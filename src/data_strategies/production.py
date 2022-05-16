from typing import List
from typing_extensions import Literal

import pandas as pd

from src.data_strategies import DataStrategy
from src.units import MW, MWh

MAX_WIND_POWER = MW(0.01)
MAX_WIND_SPEED = 11

MAX_SOLAR_POWER = MW(0.001)
SOLAR_EFFICIENCY = 0.2

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


class ImgwDataStrategy(DataStrategy):

    def __init__(self, df: pd.DataFrame = None, window_size: int = 1,
                 window_direction: Literal['forward', 'backward'] = 'forward'):
        super().__init__(df, window_size, window_direction)
        self.imgwWindDataStrategy = ImgwWindDataStrategy(df, window_size, window_direction)
        self.imgwSolarDataStrategy = ImgwSolarDataStrategy(df, window_size, window_direction)

    def process(self, idx: int) -> MWh:
        self.last_processed = self.imgwSolarDataStrategy.process(idx) + self.imgwWindDataStrategy.process(idx)
        return self.last_processed

    def observation(self, idx: int) -> List[float]:
        return self.imgwWindDataStrategy.observation(idx) + self.imgwSolarDataStrategy.observation(idx)

    def observation_size(self) -> int:
        return 2*self.window_size


def _preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.iloc[:, list(imgw_col_ids.values())]
    df.columns = list(imgw_col_ids.keys())
    return df


class ImgwWindDataStrategy(DataStrategy):
    col = 'wind_speed'
    col_idx = list(imgw_col_ids.keys()).index(col)

    def process(self, idx: int) -> MWh:
        # wind speed in meters per second
        wind_speed = self.df.iat[idx, self.col_idx]
        if wind_speed > MAX_WIND_SPEED or wind_speed < 0:
            return MWh(0)
        power = MWh(wind_speed * MAX_WIND_POWER.value / MAX_WIND_SPEED)
        self.last_processed = power
        return power

    def observation(self, idx: int) -> List[float]:
        return list(self.df.iloc[idx - self.window_size + 1:idx + 1, self.col_idx])


class ImgwSolarDataStrategy(DataStrategy):
    col = 'cloudiness'
    col_idx = list(imgw_col_ids.keys()).index(col)

    def process(self, idx: int) -> MWh:
        # cloudiness in oktas
        # https://en.wikipedia.org/wiki/Okta 
        cloudiness = self.df.iat[idx, self.col_idx]
        if cloudiness == 9:  # 9 equals lack of observation (sky obscured)
            cloudiness = 8  # 8 equals overcast
        power = MWh(MAX_SOLAR_POWER.value * (1 - cloudiness / 8))
        self.last_processed = power
        return power

    def observation(self, idx: int) -> List[float]:
        return list(self.df.iloc[idx - self.window_size + 1:idx + 1, self.col_idx])
