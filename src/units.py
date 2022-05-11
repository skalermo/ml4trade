from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True, eq=True, repr=True)
class kWh:
    value: float

    def to_cost(self, price_per_kwh: 'Currency') -> 'Currency':
        return Currency(self.value * price_per_kwh.value)

    def __add__(self, other):
        return kWh(self.value + other.value)

    def __sub__(self, other):
        return kWh(self.value - other.value)

    def __lt__(self, other):
        return self.value < other.value

    def __ge__(self, other):
        return self.value >= other.value

    def __mul__(self, other: float):
        return kWh(self.value * other)

    def __truediv__(self, other: Union['kWh', float]):
        if isinstance(other, kWh):
            return self.value / other.value
        return kWh(self.value / other)

    def __abs__(self):
        return kWh(abs(self.value))


@dataclass(frozen=True, order=True, eq=True, repr=True)
class kW:
    value: float

    def __add__(self, other: 'kW'):
        return kW(self.value + other.value)

    def __sub__(self, other: 'kW'):
        return kW(self.value - other.value)

    def to_kwh(self) -> kWh:
        return kWh(self.value)


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
