from typing import Any, List, Callable, TypeVar
from typing_extensions import Literal
from functools import wraps

import pandas as pd

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
                 window_direction: Literal['forward', 'backward'] = 'forward'):
        self.df = self.preprocess_data(df)
        self.window_size = window_size
        self.window_direction = window_direction
        self.last_processed = None

    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        return df

    def process(self, idx: int) -> float:
        raise NotImplementedError

    def observation(self, idx: int) -> List[float]:
        raise NotImplementedError

    def observation_size(self) -> int:
        return self.window_size
