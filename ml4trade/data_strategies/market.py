from typing import List

import pandas as pd

from ml4trade.data_strategies import DataStrategy, update_last_processed


class PricesPlDataStrategy(DataStrategy):
    col_name = 'Fixing I Price [PLN/MWh]'
    col_idx = 1

    def __init__(self, df: pd.DataFrame, window_size: int = 24, scheduling_hour: int = 10):
        super().__init__(df, window_size, 'backward', scheduling_hour)

    def get_column(self, df: pd.DataFrame) -> List[float]:
        return df.iloc[:, self.col_idx].tolist()

    @update_last_processed
    def process(self, idx: int) -> float:
        return self.col[idx]

    def observation(self, idx: int) -> List[float]:
        start_idx = idx - self.scheduling_hour
        end_idx = start_idx + self.window_size
        return self.col[start_idx:end_idx]
