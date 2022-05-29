import unittest
import os

from ml4trade.domain.market import UNSCHEDULED_MULTIPLIER
from ml4trade.domain.units import Currency
from utils import setup_default_market


prices_pl_path = os.path.join(os.path.dirname(__file__), 'mock_data/prices_pl.csv')


class TestMarket(unittest.TestCase):
    def setUp(self):
        self.market = setup_default_market()

    def test_get_buy_price(self):
        buy_price = self.market.get_buy_price()
        self.assertEqual(buy_price, Currency(108.27))

    def test_get_sell_price(self):
        sell_price = self.market.get_sell_price()
        self.assertEqual(sell_price, Currency(108.27))

    def test_get_buy_price_forced(self):
        buy_price_unscheduled = self.market.get_buy_price_unscheduled()
        self.assertEqual(buy_price_unscheduled, Currency(108.27) * UNSCHEDULED_MULTIPLIER)

    def test_get_sell_price_forced(self):
        sell_price_unscheduled = self.market.get_sell_price_unscheduled()
        self.assertEqual(sell_price_unscheduled, Currency(108.27) / UNSCHEDULED_MULTIPLIER)


if __name__ == '__main__':
    unittest.main()
