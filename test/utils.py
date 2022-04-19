from operator import itemgetter
import os

import pandas as pd

from src.market import EnergyMarket
from src.clock import SimulationClock
from src.simulation_env import DfsCallbacksDictType
from mock_callbacks.market_callbacks import PricesPlCallback
from mock_callbacks.production_callbacks import ImgwWindCallback, ImgwSolarCallback, imgw_col_ids


prices_pl_path = os.path.join(os.path.dirname(__file__), 'mock_data/prices_pl.csv')


def load_from_setup(setup: dict, *args) -> tuple:
    return itemgetter(*args)(setup)


def setup_default_market(df: pd.DataFrame = None, clock: SimulationClock = None) -> EnergyMarket:
    col = 'Fixing I Price [PLN/MWh]'
    if df is None:
        df = pd.read_csv(prices_pl_path, header=0, usecols=[col])

    if clock is None:
        clock = SimulationClock()

    market = EnergyMarket(df, PricesPlCallback(), clock.view())
    return market


def setup_default_dfs_and_callbacks() -> DfsCallbacksDictType:
    weather_data_path = os.path.join(os.path.dirname(__file__), 'mock_data/s_t_02_2022.csv')

    weather_df = pd.read_csv(weather_data_path, header=None, names=imgw_col_ids.keys(), usecols=imgw_col_ids.values(), encoding='cp1250')
    prices_col = 'Fixing I Price [PLN/MWh]'
    prices_df = pd.read_csv(prices_pl_path, header=0, usecols=[prices_col])

    return {
        'production': [
            (weather_df, ImgwWindCallback()),
        ],
        'market': (prices_df, PricesPlCallback()),
    }
