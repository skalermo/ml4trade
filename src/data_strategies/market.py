from typing import List

import pandas as pd

from src.data_strategies import DataStrategy, update_last_processed


class PricesPlDataStrategy(DataStrategy):
    col = 'Fixing I Price [PLN/MWh]'
    col_idx = 0

    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[[self.col]]

    @update_last_processed
    def process(self, idx: int) -> float:
        return self.df.iat[idx, self.col_idx]

    def observation(self, idx: int) -> List[float]:
        return self.df.iloc[idx - self.window_size + 1:idx + 1, self.col_idx]
