from typing import List
import random

from src.data_strategies import DataStrategy
from src.units import MW, MWh


class HouseholdEnergyConsumptionDataStrategy(DataStrategy):
    def __init__(self, window_size: int = 1):
        super().__init__(None, window_size)

        # avg energy consumption per household
        # for each hour of the day
        self.energy_consumption_MWh = [
            0.000189, 0.000184, 0.000181, 0.000181, 0.000182, 0.000185,
            0.000194, 0.000222, 0.000238, 0.000246, 0.000246, 0.000246,
            0.000248, 0.000249, 0.000246, 0.000244, 0.000244, 0.000244,
            0.000243, 0.000246, 0.000246, 0.000242, 0.000225, 0.000208
        ]

        extra_data = window_size // len(self.energy_consumption_MWh)
        self.energy_consumption_MWh += self.energy_consumption_MWh * extra_data

    def process(self, idx: int) -> MWh:
        consumed_energy = MWh(self.energy_consumption_MWh[idx % 24])
        self.last_processed = consumed_energy
        return consumed_energy * abs(1 + random.gauss(0, 0.03))

    def observation(self, idx: int) -> List[float]:
        return self.energy_consumption_MWh[idx % 24:idx % 24 + self.window_size]
