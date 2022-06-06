from typing import List

import pandas as pd

from ml4trade.data_strategies import DataStrategy, update_last_processed


class PricesPlDataStrategy(DataStrategy):
    col = 'Fixing I Price [PLN/MWh]'
    col_idx = 0

    def __init__(self, df: pd.DataFrame, window_size: int = 24, scheduling_hour: int = 10):
        super().__init__(df, window_size, 'backward', scheduling_hour)

    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[[self.col]]

    @update_last_processed
    def process(self, idx: int) -> float:
        return self.df.iat[idx, self.col_idx]

    def observation(self, idx: int) -> List[float]:
        start_idx = idx - self.scheduling_hour
        end_idx = start_idx + self.window_size
        return self.df.iloc[start_idx:end_idx, self.col_idx]
