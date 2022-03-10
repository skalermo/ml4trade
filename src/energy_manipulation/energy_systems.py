from typing import Type, List, Union

from src.custom_types import kW
from src.energy_manipulation.production import ProductionSystem
from src.energy_manipulation.consumption import ConsumptionSystem


class EnergySystems:
    def __init__(self, systems: List[Union[Type[ProductionSystem], Type[ConsumptionSystem]]] = None):
        if systems is None:
            systems = []
        self.systems = systems

    def get_production_power(self, date) -> kW:
        if not self.systems:
            return kW(0)

        power = kW(0)
        for system in self.systems:
            if isinstance(system, ProductionSystem):
                power += system.get_power(date)
        return power

    def get_consumption_power(self, date) -> kW:
        if not self.systems:
            return kW(0)

        power = kW(0)
        for system in self.systems:
            if isinstance(system, ConsumptionSystem):
                power += system.get_power(date)
        return power
