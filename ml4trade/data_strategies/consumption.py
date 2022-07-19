from typing import List
import random

from ml4trade.data_strategies import DataStrategy, update_last_processed


class HouseholdEnergyConsumptionDataStrategy(DataStrategy):
    def __init__(self, window_size: int = 24):
        super().__init__(None, window_size, 'backward')

        # avg energy consumption per 100 households
        # for each hour of the day
        self.energy_consumption_MWh = [
            0.0189, 0.0184, 0.0181, 0.0181, 0.0182, 0.0185,
            0.0194, 0.0222, 0.0238, 0.0246, 0.0246, 0.0246,
            0.0248, 0.0249, 0.0246, 0.0244, 0.0244, 0.0244,
            0.0243, 0.0246, 0.0246, 0.0242, 0.0225, 0.0208
        ]

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
