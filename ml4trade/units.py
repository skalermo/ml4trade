from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True, eq=True, repr=True)
class MWh:
    value: float

    def to_cost(self, price_per_mwh: 'Currency') -> 'Currency':
        return Currency(self.value * price_per_mwh.value)

    def __add__(self, other):
        return MWh(self.value + other.value)

    def __sub__(self, other):
        return MWh(self.value - other.value)

    def __lt__(self, other):
        return self.value < other.value

    def __ge__(self, other):
        return self.value >= other.value

    def __mul__(self, other: float):
        return MWh(self.value * other)

    def __truediv__(self, other: Union['MWh', float]):
        if isinstance(other, MWh):
            return self.value / other.value
        return MWh(self.value / other)

    def __abs__(self):
        return MWh(abs(self.value))


@dataclass(frozen=True, order=True, eq=True, repr=True)
class MW:
    value: float

    def __add__(self, other: 'MW'):
        return MW(self.value + other.value)

    def __sub__(self, other: 'MW'):
        return MW(self.value - other.value)

    def to_mwh(self) -> MWh:
        return MWh(self.value)


@dataclass(frozen=True, order=True, eq=True, repr=True)
class Currency:
    value: float

    def __add__(self, other: 'Currency'):
        return Currency(self.value + other.value)

    def __radd__(self, other: int):
        return Currency(self.value + other)

    def __sub__(self, other):
        return Currency(self.value - other.value)

    def __mul__(self, other: float) -> 'Currency':
        return Currency(self.value * other)

    def __truediv__(self, other: float) -> 'Currency':
        return Currency(self.value / other)

    def __abs__(self) -> 'Currency':
        return Currency(abs(self.value))

    def __round__(self, n=None):
        return Currency(round(self.value, n))
