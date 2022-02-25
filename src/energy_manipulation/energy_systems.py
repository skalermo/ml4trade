from typing import Type, List, Union

from src.energy_types import KW
from src.energy_manipulation.production import ProductionSystem
from src.energy_manipulation.consumption import ConsumptionSystem


class EnergySystems:
    def __init__(self, systems: List[Union[Type[ProductionSystem], Type[ConsumptionSystem]]] = None):
        if systems is None:
            systems = []
        self.systems = systems

    def get_power(self, date) -> KW:
        if not self.systems:
            return KW(0)

        power = KW(0)
        for system in self.systems:
            power += system.get_power(date)
        return power
