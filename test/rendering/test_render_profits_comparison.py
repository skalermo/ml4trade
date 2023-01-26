import unittest

import matplotlib.pyplot as plt

from utils import rendering_data_paths

from ml4trade.rendering.charts import render_profits_comparison
from ml4trade.history import History


class TestRenderProfitsComp(unittest.TestCase):
    def setUp(self) -> None:
        plt.show = lambda: ...

    def test_plotting(self):
        histories1 = [History.load(path) for path in rendering_data_paths[:2]]
        histories2 = [History.load(path) for path in rendering_data_paths[2:]]
        render_profits_comparison(
            (histories1, {'color': 'red', 'label': 'bbb'}),
            (histories2, {'color': 'cyan', 'label': 'aaa'}),
            draw_potential_profits=True,
            potential_profits_kwargs={'linestyle': 'dashed', 'label': 'reference'}
        )


if __name__ == '__main__':
    unittest.main()
