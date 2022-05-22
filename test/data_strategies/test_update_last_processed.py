import unittest
from typing import List

from ml4trade.data_strategies import DataStrategy, update_last_processed


class TestDataStrategy(DataStrategy):
    @update_last_processed
    def process(self, idx: int) -> int:
        return 42

    def observation(self, idx: int) -> List[float]:
        return [42]


class TestUpdateLastProcessed(unittest.TestCase):
    def test_sets_last_processed(self):
        t = TestDataStrategy()
        self.assertIsNone(t.last_processed)
        last = t.process(0)
        self.assertEqual(last, 42)
        self.assertEqual(t.last_processed, 42)


if __name__ == '__main__':
    unittest.main()
