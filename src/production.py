from typing import List

from src.clock import ClockView
from src.units import MWh
from src.data_strategies.base import DataStrategy


class ProductionSystem:
    def __init__(self, ds: DataStrategy, clock_view: ClockView = None):
        self.ds = ds
        self.clock_view = clock_view

    def calculate_energy(self) -> MWh:
        cur_tick = self.clock_view.cur_tick()
        return MWh(self.ds.process(cur_tick))

    def observation(self) -> List[float]:
        cur_tick = self.clock_view.cur_tick()
        return self.ds.observation(cur_tick)