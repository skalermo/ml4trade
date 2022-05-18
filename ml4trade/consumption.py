from typing import List

from ml4trade.units import MW
from ml4trade.clock import ClockView
from ml4trade.data_strategies import DataStrategy


class ConsumptionSystem:
    def __init__(self, ds: DataStrategy, clock_view: ClockView):
        self.ds = ds
        self.clock_view = clock_view

    def calculate_power(self) -> MW:
        return self.ds.process(self.clock_view.cur_datetime().hour)

    def observation(self) -> List[float]:
        return self.ds.observation(self.clock_view.cur_datetime().hour)
