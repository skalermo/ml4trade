from typing import Any, List

import pandas as pd


class DataStrategy:
    def __init__(self, df: pd.DataFrame = None, window_size: int = 1):
        self.df = df
        self._window_size = window_size

    def window_size(self) -> int:
        return self._window_size

    def preprocess_data(self) -> None:
        pass

    def processed_columns(self) -> List[str]:
        pass

    def process(self, idx: int) -> Any:
        raise NotImplementedError

    def observation(self, idx: int) -> List[float]:
        raise NotImplementedError
