from typing import List

from src.units import MWh
from src.clock import ClockView
from src.data_strategies import DataStrategy


class ConsumptionSystem:
    def __init__(self, ds: DataStrategy, clock_view: ClockView):
        self.ds = ds
        self.clock_view = clock_view

    def calculate_energy(self) -> MWh:
        return MWh(self.ds.process(self.clock_view.cur_datetime().hour))

    def observation(self) -> List[float]:
        return self.ds.observation(self.clock_view.cur_datetime().hour)
