from datetime import datetime
from typing import Any

from pandas import DataFrame


class Callback:
    def preprocess_data(self, df: DataFrame) -> None:
        raise NotImplementedError

    def processed_columns(self) -> list:
        raise NotImplementedError

    def process(self, df: DataFrame, _datetime: datetime) -> Any:
        raise NotImplementedError
