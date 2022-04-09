from typing import Any

from pandas import DataFrame


class Callback:
    def preprocess_data(self, df: DataFrame) -> None:
        raise NotImplementedError

    def processed_columns(self) -> list[str]:
        raise NotImplementedError

    def process(self, df: DataFrame, idx: int) -> Any:
        raise NotImplementedError
