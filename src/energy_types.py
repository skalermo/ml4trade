from __future__ import annotations


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


class KWh:
    def __init__(self, value: int):
        self.value = value


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
