from typing import List

from ml4trade.domain.units import MWh
from ml4trade.domain.clock import ClockView
from ml4trade.data_strategies import DataStrategy


class ConsumptionSystem:
    def __init__(self, ds: DataStrategy, clock_view: ClockView):
        self.ds = ds
        self.clock_view = clock_view

    def calculate_energy(self) -> MWh:
        return MWh(self.ds.process(self.clock_view.cur_datetime().hour))

    def observation(self) -> List[float]:
        return self.ds.observation(self.clock_view.cur_datetime().hour)
