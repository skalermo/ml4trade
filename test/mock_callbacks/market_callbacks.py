from pandas import DataFrame

from src.callback import Callback
from src.custom_types import Currency


class PricesPlCallback(Callback):

    def preprocess_data(self, df: DataFrame) -> None:
        pass

    def processed_columns(self) -> list:
        return ['Fixing I Price [PLN/MWh]']

    def process(self, df: DataFrame, idx: int) -> Currency:
        # 2016-01-01 00:00:00
        val = df.loc[idx, self.processed_columns()[0]]
        return Currency(val)
