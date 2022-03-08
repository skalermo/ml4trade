from typing import Callable

from src.types import kW


def _default_callback(date):
    return kW(5)


class ProductionSystem:
    def get_power(self, date, callback: Callable = _default_callback) -> kW:
        return callback(date)
