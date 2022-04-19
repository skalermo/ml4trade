from typing import List
import random

from src.custom_types import kW
from src.clock import ClockView

# avg energy consumption per household
# for each hour of the day
energy_consumption_kWh = [
    0.189, 0.184, 0.181, 0.181, 0.182, 0.185,
    0.194, 0.222, 0.238, 0.246, 0.246, 0.246,
    0.248, 0.249, 0.246, 0.244, 0.244, 0.244,
    0.243, 0.246, 0.246, 0.242, 0.225, 0.208
]


class ConsumptionSystem:
    def __init__(self, clock_view: ClockView):
        self.clock_view = clock_view

    def calculate_power(self) -> kW:
        return self._calculate_power(self.clock_view.cur_datetime().hour)

    @staticmethod
    def _calculate_power(idx: int) -> kW:
        consumed_energy = energy_consumption_kWh[idx]
        return kW(consumed_energy * abs(1 + random.gauss(0, 0.03)))

    def observation(self) -> List[float]:
        cur_tick = self.clock_view.cur_tick()
        res = [self._calculate_power(tick).value for tick in range(cur_tick - 24 + 1, cur_tick + 1)]
        return res
