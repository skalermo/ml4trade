from typing import List
from typing_extensions import Literal

import pandas as pd

from ml4trade.data_strategies import DataStrategy
from ml4trade.units import MW

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
                 window_direction: Literal['forward', 'backward'] = 'forward', max_solar_power: MW = MW(0.001),
                 solar_efficiency: float = 0.2, max_wind_power: MW = MW(0.01), max_wind_speed: float = 11):
        super().__init__(df, window_size, window_direction)
        self.imgwWindDataStrategy = ImgwWindDataStrategy(df, window_size, window_direction, max_wind_power,
                                                         max_wind_speed)
        self.imgwSolarDataStrategy = ImgwSolarDataStrategy(df, window_size, window_direction, max_solar_power,
                                                           solar_efficiency)

    def process(self, idx: int) -> MW:
        return self.imgwSolarDataStrategy.process(idx) + self.imgwWindDataStrategy.process(idx)

    def observation(self, idx: int) -> List[float]:
        return self.imgwWindDataStrategy.observation(idx) + self.imgwSolarDataStrategy.observation(idx)

    def observation_size(self) -> int:
        return 2 * self.window_size


def _preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.iloc[:, list(imgw_col_ids.values())]
    df.columns = list(imgw_col_ids.keys())
    return df


class ImgwWindDataStrategy(DataStrategy):

    def __init__(self, df: pd.DataFrame = None, window_size: int = 1,
                window_direction: Literal['forward', 'backward'] = 'forward', max_wind_power: MW = MW(0.01),
                max_wind_speed: float = 11):
        super().__init__(df, window_size, window_direction)
        self.max_wind_power = max_wind_power
        self.max_wind_speed = max_wind_speed

    col = 'wind_speed'
    col_idx = list(imgw_col_ids.keys()).index(col)

    def process(self, idx: int) -> MW:
        # wind speed in meters per second
        wind_speed = self.df.iat[idx, self.col_idx]
        if wind_speed > self.max_wind_speed or wind_speed < 0:
            return MW(0)
        power = MW(wind_speed * self.max_wind_power.value / self.max_wind_speed)
        return power

    def observation(self, idx: int) -> List[float]:
        return list(self.df.iloc[idx - self.window_size + 1:idx + 1, self.col_idx])


class ImgwSolarDataStrategy(DataStrategy):

    def __init__(self, df: pd.DataFrame = None, window_size: int = 1,
                window_direction: Literal['forward', 'backward'] = 'forward', max_solar_power: MW = MW(0.001),
                solar_efficiency: float = 0.2):

        super().__init__(df, window_size, window_direction)
        self.max_solar_power = max_solar_power
        self.solar_efficiency = solar_efficiency

    col = 'cloudiness'
    col_idx = list(imgw_col_ids.keys()).index(col)

    def process(self, idx: int) -> MW:
        # cloudiness in oktas
        # https://en.wikipedia.org/wiki/Okta 
        cloudiness = self.df.iat[idx, self.col_idx]
        if cloudiness == 9:  # 9 equals lack of observation (sky obscured)
            cloudiness = 8  # 8 equals overcast
        power = MW(self.max_solar_power.value * (1 - cloudiness / 8) * self.solar_efficiency)
        return power

    def observation(self, idx: int) -> List[float]:
        return list(self.df.iloc[idx - self.window_size + 1:idx + 1, self.col_idx])
