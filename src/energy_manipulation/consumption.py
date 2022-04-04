from datetime import time
import random

from src.custom_types import kW

# avg energy consumption per household
# for each hour of the day
energy_consumption_kWh = [
    0.189, 0.184, 0.181, 0.181, 0.182, 0.185,
    0.194, 0.222, 0.238, 0.246, 0.246, 0.246,
    0.248, 0.249, 0.246, 0.244, 0.244, 0.244,
    0.243, 0.246, 0.246, 0.242, 0.225, 0.208
]


class ConsumptionSystem:
    def calculate_power(self, _time: time) -> kW:
        return self._calculate_power(_time)

    @staticmethod
    def _calculate_power(_time: time) -> kW:
        consumed_energy = energy_consumption_kWh[_time.hour]
        return kW(consumed_energy * abs(1 + random.gauss(0, 0.03)))
