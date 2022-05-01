from typing import List

import pandas as pd

from src.data_strategies import DataStrategy
from src.units import Currency


class PricesPlDataStrategy(DataStrategy):
    col = 'Fixing I Price [PLN/MWh]'

    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[[self.col]]

    def process(self, idx: int) -> Currency:
        val = self.df.loc[idx, self.col]
        return Currency(val)

    def observation(self, idx: int) -> List[float]:
        res = [self.process(i).value for i in range(idx - self._window_size + 1, idx + 1)]
        return res
