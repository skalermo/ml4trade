from pandas import DataFrame
from src.custom_types import kW
from src.callback import Callback


class ProductionSystem:
    def __init__(self, df: DataFrame, cb: Callback):
        self.df = df
        self.cb = cb
        self.cb.preprocess_data(df)

    def calculate_power(self, idx: int) -> kW:
        return self.cb.process(self.df, idx)
