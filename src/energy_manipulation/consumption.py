from typing import Callable

from src.custom_types import kW


def _default_callback(date):
    return kW(-10)


class ConsumptionSystem:
    def get_power(self, date, callback: Callable = _default_callback) -> kW:
        return callback(date)
