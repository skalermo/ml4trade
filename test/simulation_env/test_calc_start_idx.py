import unittest

from ml4trade.utils import calc_tick_offset
from ml4trade.domain.constants import SCHEDULING_TIME

from utils import setup_default_data_strategies


class TestCalcStartIdx(unittest.TestCase):
    def test_start_idx_points_to_scheduling_hour(self):
        dss = setup_default_data_strategies()
        start_idx = calc_tick_offset(list(dss.values()), SCHEDULING_TIME)
        self.assertEqual(start_idx % 24, SCHEDULING_TIME.hour)


if __name__ == '__main__':
    unittest.main()
