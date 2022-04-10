import unittest
import os

import pandas as pd

from src.market import EnergyMarket, FORCED_MULTIPLIER
from src.clock import SimulationClock
from src.custom_types import Currency
from mock_callbacks.market_callbacks import PricesPlCallback


prices_pl_path = os.path.join(os.path.dirname(__file__), 'mock_data/prices_pl.csv')


class TestMarket(unittest.TestCase):
    def setUp(self):
        col = 'Fixing I Price [PLN/MWh]'
        self.df = pd.read_csv(prices_pl_path, header=0, usecols=[col])
        self.clock = SimulationClock()
        self.market = EnergyMarket(self.df, PricesPlCallback(), self.clock.view())

    def test_get_buy_price(self):
        buy_price = self.market.get_buy_price()
        self.assertEqual(buy_price, Currency(108.27))

    def test_get_sell_price(self):
        sell_price = self.market.get_sell_price()
        self.assertEqual(sell_price, Currency(108.27))

    def test_get_buy_price_forced(self):
        buy_price_forced = self.market.get_buy_price_forced()
        self.assertEqual(buy_price_forced, Currency(108.27) * FORCED_MULTIPLIER)

    def test_get_sell_price_forced(self):
        sell_price_forced = self.market.get_sell_price_forced()
        self.assertEqual(sell_price_forced, Currency(108.27) / FORCED_MULTIPLIER)


if __name__ == '__main__':
    unittest.main()
