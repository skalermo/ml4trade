from typing import List

import pandas as pd

from ml4trade.data_strategies import DataStrategy
from ml4trade.units import Currency


class PricesPlDataStrategy(DataStrategy):
    col = 'Fixing I Price [PLN/MWh]'
    col_idx = 0

    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[[self.col]]

    def process(self, idx: int) -> Currency:
        val = self.df.iat[idx, self.col_idx]
        return Currency(val)

    def observation(self, idx: int) -> List[float]:
        return self.df.iloc[idx - self.window_size + 1:idx + 1, self.col_idx]
