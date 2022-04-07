import unittest
import os

import pandas as pd

from src.market import EnergyMarket


class TestMarket(unittest.TestCase):
    def test_constructor(self):
        path = os.path.join(os.path.dirname(__file__), 'ref_data/prices_pl.csv')
        df = pd.read_csv(path)
        EnergyMarket(df, window_size=5)


if __name__ == '__main__':
    unittest.main()
