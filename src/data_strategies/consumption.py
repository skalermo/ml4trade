from typing import List
from typing_extensions import Literal
import random

import pandas as pd

from src.data_strategies import DataStrategy
from src.units import kW


class HouseholdEnergyConsumptionDataStrategy(DataStrategy):
    def __init__(self, window_size: int = 1):
        super().__init__(None, window_size)

        # avg energy consumption per household
        # for each hour of the day
        self.energy_consumption_kWh = [
            0.189, 0.184, 0.181, 0.181, 0.182, 0.185,
            0.194, 0.222, 0.238, 0.246, 0.246, 0.246,
            0.248, 0.249, 0.246, 0.244, 0.244, 0.244,
            0.243, 0.246, 0.246, 0.242, 0.225, 0.208
        ]

        extra_data = window_size // len(self.energy_consumption_kWh) + 1
        self.energy_consumption_kWh += self.energy_consumption_kWh * extra_data

    def process(self, idx: int) -> kW:
        consumed_energy = self.energy_consumption_kWh[idx % 24]
        return kW(consumed_energy * abs(1 + random.gauss(0, 0.03)))

    def observation(self, idx: int) -> List[float]:
        return self.energy_consumption_kWh[idx % 24:idx % 24 + self._window_size]
