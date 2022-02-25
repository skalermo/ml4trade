from typing import Callable

from src.energy_types import KW


def _default_callback(date):
    return KW(-10)


class ConsumptionSystem:
    def get_power(self, date, callback: Callable = _default_callback) -> KW:
        return callback(date)
