from typing import List

import pandas as pd
from typing_extensions import Literal

from ml4trade.data_strategies import DataStrategy, update_last_processed
from ml4trade.domain.units import MW

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

    def __init__(self, df: pd.DataFrame, window_size: int,
                 max_solar_power: MW, solar_efficiency: float, max_wind_power: MW, max_wind_speed: float,
                 window_direction: Literal['forward', 'backward'] = 'forward'):
        super().__init__(df, window_size, window_direction)
        self.imgwWindDataStrategy = ImgwWindDataStrategy(df, window_size, max_wind_power, max_wind_speed,
                                                         window_direction)
        self.imgwSolarDataStrategy = ImgwSolarDataStrategy(df, window_size, max_solar_power, solar_efficiency,
                                                           window_direction)

    @update_last_processed
    def process(self, idx: int) -> float:
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

    def __init__(self, df: pd.DataFrame, window_size: int,
                 max_wind_power: MW, max_wind_speed: float,
                 window_direction: Literal['forward', 'backward'] = 'forward'):
        super().__init__(df, window_size, window_direction)
        self.max_wind_power = max_wind_power
        self.max_wind_speed = max_wind_speed

    col = 'wind_speed'
    col_idx = list(imgw_col_ids.keys()).index(col)

    @update_last_processed
    def process(self, idx: int) -> float:
        # wind speed in meters per second
        wind_speed = self.df.iat[idx, self.col_idx]
        return self.calculate_power_value(wind_speed, self.max_wind_speed, self.max_wind_power.value)

    @staticmethod
    def calculate_power_value(wind_speed: float, max_wind_speed: float, max_wind_power_value: float) -> float:
        if wind_speed > max_wind_speed or wind_speed < 0:
            return 0
        return wind_speed * max_wind_power_value / max_wind_speed

    def observation(self, idx: int) -> List[float]:
        start_idx = idx + 24 - self.scheduling_hour
        end_idx = start_idx + self.window_size
        return list(self.df.iloc[start_idx:end_idx, self.col_idx])


class ImgwSolarDataStrategy(DataStrategy):

    def __init__(self, df: pd.DataFrame, window_size: int,
                 max_solar_power: MW, solar_efficiency: float,
                 window_direction: Literal['forward', 'backward'] = 'forward'):
        super().__init__(df, window_size, window_direction)
        self.max_solar_power = max_solar_power
        self.solar_efficiency = solar_efficiency

    col = 'cloudiness'
    col_idx = list(imgw_col_ids.keys()).index(col)

    @update_last_processed
    def process(self, idx: int) -> float:
        cloudiness = self.df.iat[idx, self.col_idx]
        return self.calculate_power_value(cloudiness, self.max_solar_power.value, self.solar_efficiency)

    @staticmethod
    def calculate_power_value(cloudiness: int, max_solar_power_value: float, solar_efficiency: float) -> float:
        # cloudiness in oktas
        # https://en.wikipedia.org/wiki/Okta
        if cloudiness == 9:  # 9 equals lack of observation (sky obscured)
            cloudiness = 8  # 8 equals overcast
        return max_solar_power_value * (1 - cloudiness / 8) * solar_efficiency

    def observation(self, idx: int) -> List[float]:
        start_idx = idx + 24 - self.scheduling_hour
        end_idx = start_idx + self.window_size
        return list(self.df.iloc[start_idx:end_idx, self.col_idx])
