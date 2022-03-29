from datetime import time
from typing import Callable
import pandas
import random
from src.custom_types import kW


def _default_callback(time):
    return kW(-10)


class ConsumptionSystem:

    def get_power(self, _time: time, callback: Callable = _default_callback) -> kW:
        df = pandas.read_table('https://github.com/skalermo/ml4trade/blob/consumption_system/consumption_energy.txt')

        return callback(time)
