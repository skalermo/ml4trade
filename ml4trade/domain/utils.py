from datetime import datetime, time
from typing import Dict, Tuple

from ml4trade.data_strategies import DataStrategy
from .battery import Battery
from .clock import SimulationClock
from .consumption import ConsumptionSystem
from .market import EnergyMarket
from .production import ProductionSystem
from .prosumer import Prosumer
from .units import Currency, MWh


def setup_systems(
        data_strategies: Dict[str, DataStrategy],
        start_tick: int,
        prosumer_init_balance: Currency,
        start_datetime: datetime,
        scheduling_time: time,
        action_replacement_time: time,
        battery_init_charge: MWh,
        battery_efficiency: float,
        battery_capacity: MWh,
) -> Tuple[SimulationClock, Prosumer, EnergyMarket, ProductionSystem, ConsumptionSystem]:
    clock = SimulationClock(start_datetime, scheduling_time, action_replacement_time, start_tick)
    battery = Battery(battery_capacity, battery_efficiency, battery_init_charge)
    production_system = ProductionSystem(data_strategies.get('production'), clock.view())
    consumption_system = ConsumptionSystem(data_strategies.get('consumption'), clock.view())
    market = EnergyMarket(data_strategies.get('market'), clock.view())

    prosumer = Prosumer(battery, production_system, consumption_system,
                        clock.view(), prosumer_init_balance, market)
    return clock, prosumer, market, production_system, consumption_system
