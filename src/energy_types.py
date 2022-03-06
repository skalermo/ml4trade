from __future__ import annotations


def to_ah(other: float) -> Ah:
    return Ah(other)


def to_kw(other: float) -> KW:
    return KW(other)


def to_kwh(other: int) -> KWh:
    return KWh(other)


class Ah:
    def __init__(self, value: float):
        self.value = value

    def __add__(self, other: Ah):
        return Ah(self.value + other.value)

    def __sub__(self, other: Ah):
        return Ah(self.value - other.value)

    def __gt__(self, other: Ah):
        return self.value > other.value

    def __ge__(self, other: Ah):
        return self.value >= other.value

    def __lt__(self, other: Ah):
        return self.value < other.value

    def __eq__(self, other: Ah):
        return self.value == other.value

    def __neg__(self):
        return self.value * -1


class KWh:
    def __init__(self, value: int):
        self.value = value

    def __mul__(self, other: float):
        return self.value * other


class KW:
    def __init__(self, value: float):
        self.value = value

    def __add__(self, other: KW):
        return KW(self.value + other.value)

    def __sub__(self, other: KW):
        return KW(self.value - other.value)

    def __gt__(self, other: KW):
        return self.value > other.value

    def __ge__(self, other: KW):
        return self.value >= other.value

    def __lt__(self, other: KW):
        return self.value < other.value

    def __eq__(self, other: KW):
        return self.value == other.value
