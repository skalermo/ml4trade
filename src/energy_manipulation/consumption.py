from datetime import time
from typing import Callable
import pandas
import random

from pandas import DataFrame

from src.custom_types import kW

ENERGY_CONSUMPTION_PATH = './consumption_energy.txt'


def _default_callback(_time: time, df: DataFrame) -> kW:
    consumed_energy = df.iat[_time.hour, 1]
    return kW(consumed_energy * abs(1 + random.gauss(0, 0.03)))


class ConsumptionSystem:

    def get_power(self, _time: time, callback: Callable = _default_callback) -> kW:
        df = pandas.read_table(ENERGY_CONSUMPTION_PATH)
        return callback(_time, df)
