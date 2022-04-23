from typing import List

from pandas import DataFrame

from src.clock import ClockView
from src.custom_types import kW
from src.callback import Callback


class ProductionSystem:
    def __init__(self, df: DataFrame, cb: Callback, clock_view: ClockView = None):
        self.df = df
        self.cb = cb
        self.clock_view = clock_view

    def calculate_power(self) -> kW:
        cur_tick = self.clock_view.cur_tick()
        return self.cb.process(self.df, cur_tick)

    def observation(self) -> List[float]:
        cur_tick = self.clock_view.cur_tick()
        return self.cb.observation(self.df, cur_tick)
