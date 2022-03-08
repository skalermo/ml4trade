from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True, order=True, eq=True, repr=True)
class Ah:
    value: float

    def __add__(self, other):
        return Ah(self.value + other.value)

    def __sub__(self, other):
        return Ah(self.value - other.value)


@dataclass(frozen=True, order=True, eq=True, repr=True)
class kWh:
    value: float

    def to_cost(self, price_per_kwh: Currency) -> Currency:
        return Currency(self.value * price_per_kwh.value)


@dataclass(frozen=True, order=True, eq=True, repr=True)
class kW:
    value: float

    def __add__(self, other: kW):
        return kW(self.value + other.value)

    def __sub__(self, other: kW):
        return kW(self.value - other.value)

    def to_kwh(self) -> kWh:
        return kWh(self.value)


@dataclass(frozen=True, order=True, eq=True, repr=True)
class Currency:
    value: float