from operator import itemgetter
import os
from typing import Dict

import pandas as pd

from ml4trade.market import EnergyMarket
from ml4trade.clock import SimulationClock
from ml4trade.data_strategies import DataStrategy, PricesPlDataStrategy, ImgwSolarDataStrategy, HouseholdEnergyConsumptionDataStrategy, imgw_col_ids
from ml4trade.consumption import ConsumptionSystem


prices_pl_path = os.path.join(os.path.dirname(__file__), 'mock_data/prices_pl.csv')


def load_from_setup(setup: dict, *args) -> tuple:
    return itemgetter(*args)(setup)


def setup_default_market(df: pd.DataFrame = None, clock: SimulationClock = None) -> EnergyMarket:
    if df is None:
        df = pd.read_csv(prices_pl_path, header=0)

    if clock is None:
        clock = SimulationClock()

    market = EnergyMarket(PricesPlDataStrategy(df), clock.view())
    return market


def setup_default_consumption_system(clock: SimulationClock = None, window_size: int = 1) -> ConsumptionSystem:
    if clock is None:
        clock = SimulationClock()
    return ConsumptionSystem(HouseholdEnergyConsumptionDataStrategy(window_size), clock.view())


def setup_default_data_strategies() -> Dict[str, DataStrategy]:
    weather_data_path = os.path.join(os.path.dirname(__file__), 'mock_data/s_t_02-03_2022.csv')

    weather_df = pd.read_csv(weather_data_path, header=None, encoding='cp1250')
    prices_df = pd.read_csv(prices_pl_path, header=0)

    return {
        'production': ImgwSolarDataStrategy(weather_df),
        'market': PricesPlDataStrategy(prices_df, window_size=24, window_direction='backward'),
        'consumption': HouseholdEnergyConsumptionDataStrategy(),
    }
