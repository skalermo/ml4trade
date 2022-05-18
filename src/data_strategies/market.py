from typing import List

import pandas as pd

from src.data_strategies import DataStrategy
from src.units import Currency


class PricesPlDataStrategy(DataStrategy):
    col = 'Fixing I Price [PLN/MWh]'
    col_idx = 0

    def __init__(self, df: pd.DataFrame, scheduling_hour: int = 10):
        super().__init__(df, 24, 'backward')
        self.scheduling_hour = scheduling_hour

    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[[self.col]]

    def process(self, idx: int) -> Currency:
        val = self.df.iat[idx, self.col_idx]
        return Currency(val)

    def observation(self, idx: int) -> List[float]:
        start_idx = idx - self.scheduling_hour
        end_idx = start_idx + self.window_size
        return self.df.iloc[start_idx:end_idx, self.col_idx]
