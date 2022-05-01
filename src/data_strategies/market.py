from typing import List

from src.data_strategies import DataStrategy
from src.units import Currency


class PricesPlDataStrategy(DataStrategy):
    def preprocess_data(self) -> None:
        pass

    def processed_columns(self) -> list:
        return ['Fixing I Price [PLN/MWh]']

    def process(self, idx: int) -> Currency:
        # 2016-01-01 00:00:00
        val = self.df.loc[idx, self.processed_columns()[0]]
        return Currency(val)

    def observation(self, idx: int) -> List[float]:
        res = [self.process(i).value for i in range(idx - self._window_size + 1, idx + 1)]
        return res
