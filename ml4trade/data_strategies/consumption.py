from typing import List
import random

from ml4trade.data_strategies import DataStrategy, update_last_processed


class HouseholdEnergyConsumptionDataStrategy(DataStrategy):
    def __init__(self, window_size: int = 24):
        super().__init__(None, window_size, 'backward')

        # avg energy consumption per 100 households
        # for each hour of the day
        self.energy_consumption_MWh = [
            0.000189, 0.000184, 0.000181, 0.000181, 0.000182, 0.000185,
            0.000194, 0.000222, 0.000238, 0.000246, 0.000246, 0.000246,
            0.000248, 0.000249, 0.000246, 0.000244, 0.000244, 0.000244,
            0.000243, 0.000246, 0.000246, 0.000242, 0.000225, 0.000208
        ]

        self.energy_consumption_MWh = list(map(lambda x: x * 100, self.energy_consumption_MWh))
        extra_data = window_size // len(self.energy_consumption_MWh)
        self.energy_consumption_MWh += self.energy_consumption_MWh * extra_data

    @update_last_processed
    def process(self, idx: int) -> float:
        consumed_energy = self.energy_consumption_MWh[idx % 24]
        return consumed_energy * abs(1 + random.gauss(0, 0.03))

    def observation(self, idx: int) -> List[float]:
        start_idx = idx % 24 - self.scheduling_hour
        end_idx = start_idx + self.window_size
        return self.energy_consumption_MWh[start_idx:end_idx]
