from datetime import time
from typing import Callable
import pandas
import random
from src.custom_types import kW


def _default_callback(hour, df):
    consumed_energy = df.iat[hour, 1]
    return kW(consumed_energy*abs(1+random.gauss(0, 0.3)))


class ConsumptionSystem:

    def get_power(self, _time: time, callback: Callable = _default_callback) -> kW:
        # df = pandas.read_table(r'https://github.com/skalermo/ml4trade/blob/consumption_system/consumption_energy.txt')
        df = pandas.read_table(r'C:\Users\agnie\Desktop\Agnieszka\Nauka\Informatyka\magisterka\mgr\consumption_energy.txt')
        return callback(_time.hour, df)
