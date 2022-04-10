from operator import itemgetter
import os

import pandas as pd

from src.market import EnergyMarket
from src.clock import SimulationClock
from mock_callbacks.market_callbacks import PricesPlCallback


prices_pl_path = os.path.join(os.path.dirname(__file__), 'mock_data/prices_pl.csv')


def load_from_setup(setup: dict, *args) -> tuple:
    return itemgetter(*args)(setup)


def setup_default_market(df: pd.DataFrame = None, clock: SimulationClock = None) -> EnergyMarket:
    col = 'Fixing I Price [PLN/MWh]'
    if df is None:
        _df = pd.read_csv(prices_pl_path, header=0, usecols=[col])
    else:
        _df = df

    if clock is None:
        _clock = SimulationClock()
    else:
        _clock = clock

    market = EnergyMarket(_df, PricesPlCallback(), _clock.view())
    return market
