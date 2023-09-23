from typing import List, Callable, TypeVar
from typing_extensions import Literal
from functools import wraps

import pandas as pd
from gymnasium.utils import seeding

from ml4trade.domain.constants import SCHEDULING_TIME

C = TypeVar('C', bound=Callable)


# decorator for saving result returned by fn()
def update_last_processed(fn: C) -> C:
    @wraps(fn)
    def inner(*args, **kwargs):
        res = fn(*args, **kwargs)
        self = args[0]
        self.last_processed = res
        return res
    return inner


class DataStrategy:
    def __init__(self, df: pd.DataFrame = None, window_size: int = 1,
                 window_direction: Literal['forward', 'backward'] = 'forward',
                 scheduling_hour: int = SCHEDULING_TIME.hour):
        self.df = df
        self.col = self.get_column(df)
        self.window_size = window_size
        self.window_direction = window_direction
        self.scheduling_hour = scheduling_hour
        self.last_processed = None
        self._rng = None

    @property
    def rng(self):
        if self._rng is None:
            self._rng, seed = seeding.np_random()
        return self._rng

    def set_seed(self, seed: int):
        self._rng, seed = seeding.np_random(seed)

    def get_column(self, df: pd.DataFrame) -> List[float]:
        pass

    def process(self, idx: int) -> float:
        raise NotImplementedError

    def observation(self, idx: int) -> List[float]:
        raise NotImplementedError

    def observation_size(self) -> int:
        return self.window_size
