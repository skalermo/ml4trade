import os
from operator import itemgetter
from typing import Dict

import pandas as pd

from ml4trade.data_strategies import DataStrategy, PricesPlDataStrategy, ImgwSolarDataStrategy, \
    HouseholdEnergyConsumptionDataStrategy
from ml4trade.domain.battery import Battery
from ml4trade.domain.clock import SimulationClock
from ml4trade.domain.constants import START_TIME, END_TIME, SCHEDULING_TIME, ACTION_REPLACEMENT_TIME
from ml4trade.domain.consumption import ConsumptionSystem
from ml4trade.domain.market import EnergyMarket
from ml4trade.domain.units import Currency, MWh
from ml4trade.domain.units import MW
from ml4trade.simulation_env import SimulationEnv

prices_pl_path = os.path.join(os.path.dirname(__file__), 'mock_data/prices_pl.csv')


def load_from_setup(setup: dict, *args) -> tuple:
    return itemgetter(*args)(setup)


def setup_default_market(df: pd.DataFrame = None, clock: SimulationClock = None) -> EnergyMarket:
    if df is None:
        df = pd.read_csv(prices_pl_path, header=0)

    if clock is None:
        clock = setup_default_clock()

    market = EnergyMarket(PricesPlDataStrategy(df), clock.view())
    return market


def setup_default_consumption_system(clock: SimulationClock = None, window_size: int = 1) -> ConsumptionSystem:
    if clock is None:
        clock = setup_default_clock()
    return ConsumptionSystem(HouseholdEnergyConsumptionDataStrategy(window_size), clock.view())


def setup_default_data_strategies() -> Dict[str, DataStrategy]:
    weather_data_path = os.path.join(os.path.dirname(__file__), 'mock_data/s_t_02-03_2022.csv')

    weather_df = pd.read_csv(weather_data_path, header=None, encoding='cp1250')
    prices_df = pd.read_csv(prices_pl_path, header=0)

    return {
        'production': ImgwSolarDataStrategy(weather_df, window_size=24, max_solar_power=MW(0.001),
                                            solar_efficiency=0.2),
        'market': PricesPlDataStrategy(prices_df),
        'consumption': HouseholdEnergyConsumptionDataStrategy(),
    }


def setup_default_battery() -> Battery:
    return Battery(MWh(0.1), 1.0, MWh(0.05))


def setup_default_clock(start_datetime=START_TIME) -> SimulationClock:
    return SimulationClock(
        start_datetime=start_datetime,
        scheduling_time=SCHEDULING_TIME,
        action_replacement_time=ACTION_REPLACEMENT_TIME
    )


def setup_default_simulation_env(
        data_strategies=setup_default_data_strategies(),
        start_datetime=START_TIME,
        end_datetime=END_TIME,
        scheduling_time=SCHEDULING_TIME,
        action_replacement_time=ACTION_REPLACEMENT_TIME,
        prosumer_init_balance=Currency(0),
        battery_capacity=MWh(0.1),
        battery_init_charge=MWh(0),
        battery_efficiency=1.0,
        start_tick=None,
) -> SimulationEnv:
    return SimulationEnv(
        data_strategies=data_strategies,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        scheduling_time=scheduling_time,
        action_replacement_time=action_replacement_time,
        prosumer_init_balance=prosumer_init_balance,
        battery_capacity=battery_capacity,
        battery_init_charge=battery_init_charge,
        battery_efficiency=battery_efficiency,
        start_tick=start_tick,
    )
