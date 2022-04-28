from typing import List
import random

from src.custom_types import kW
from src.clock import ClockView
from src.data_strategies import DataStrategy


class ConsumptionSystem:
    def __init__(self, ds: DataStrategy, clock_view: ClockView):
        self.ds = ds
        self.clock_view = clock_view

    def calculate_power(self) -> kW:
        return self.ds.process(self.clock_view.cur_datetime().hour)
        # return self._calculate_power(self.clock_view.cur_datetime().hour)

    # @staticmethod
    # def _calculate_power(idx: int) -> kW:
    #     consumed_energy = energy_consumption_kWh[idx % 24]
    #     return kW(consumed_energy * abs(1 + random.gauss(0, 0.03)))

    def observation(self) -> List[float]:
        return self.ds.observation(self.clock_view.cur_datetime().hour)
        # res = [self._calculate_power(tick).value for tick in range(cur_tick - 24 + 1, cur_tick + 1)]
        # return res
