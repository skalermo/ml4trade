import unittest

from ml4trade.units import Currency
from utils import setup_default_data_strategies


class TestMarketDataStrategy(unittest.TestCase):
    def setUp(self):
        self.market_ds = setup_default_data_strategies()['market']

    def test_process(self):
        self.assertEqual(self.market_ds.process(7), 98.12)

    def test_observation(self):
        expected = [108.27, 94.74, 85.05, 79.35, 75.17, 79.5,
                    82.96, 98.12, 105.43, 120.09, 134.99, 137.05,
                    138.5, 142.25, 141.28, 142.24, 147.92, 145.02,
                    145.63, 145.02, 142.28, 134.39, 119.72, 105.68]
        self.assertListEqual(list(self.market_ds.observation(10)), expected)


if __name__ == '__main__':
    unittest.main()
