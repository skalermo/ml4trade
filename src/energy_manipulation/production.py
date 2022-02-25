from typing import Callable

from src.energy_types import KW


def _default_callback(date):
    return KW(5)


class ProductionSystem:
    def get_power(self, date, callback: Callable = _default_callback) -> KW:
        return callback(date)
