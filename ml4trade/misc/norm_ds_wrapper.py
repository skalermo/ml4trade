from typing import List, Union

from ml4trade.data_strategies import (
    DataStrategy,
    HouseholdEnergyConsumptionDataStrategy,
    ImgwWindDataStrategy,
    ImgwSolarDataStrategy,
    PricesPlDataStrategy,
    update_last_processed,
)


class DataStrategyWrapper:
    def __init__(self, ds: DataStrategy):
        super().__init__()
        self.ds = ds

    @update_last_processed
    def process(self, idx: int) -> float:
        return self.ds.process(idx)

    def observation(self, idx: int) -> List[float]:
        return self.ds.observation(idx)

    def observation_size(self) -> int:
        return self.ds.observation_size()

    def __getattr__(self, item):
        return getattr(self.ds, item)


class DummyWrapper(DataStrategyWrapper):
    def __init__(self, ds: DataStrategy):
        super().__init__(ds)

    def observation(self, idx: int) -> List[float]:
        return []

    def observation_size(self) -> int:
        return 0


class MarketWrapper(DataStrategyWrapper):
    def __init__(self, ds: PricesPlDataStrategy):
        super().__init__(ds)
        self.col_mean = ds.df.iloc[:, ds.col_idx].mean()
        self.col_std = ds.df.iloc[:, ds.col_idx].std()

    @staticmethod
    def _minmax_scale(obs: list):
        min_val = min(obs)
        max_val = max(obs)
        return list(map(lambda x: (x - min_val) / (max_val - min_val), obs))

    def observation(self, idx: int) -> List[float]:
        obs = self.ds.observation(idx)
        # return list(map(lambda x: (x - self.col_mean) / self.col_std, obs))
        return self._minmax_scale(obs)


class ConsumptionWrapper(DataStrategyWrapper):
    def __init__(self, ds: HouseholdEnergyConsumptionDataStrategy):
        super().__init__(ds)

    def observation(self, idx: int) -> List[float]:
        obs = self.ds.observation(idx)
        return list(map(lambda x: x * 1000 / self.ds.household_number, obs))
        # return obs


class WeatherWrapper(DataStrategyWrapper):
    def __init__(self, ds: Union[ImgwSolarDataStrategy, ImgwWindDataStrategy]):
        super().__init__(ds)
        self.col_mean = ds.df.iloc[:, ds.col_idx].mean()
        self.col_std = ds.df.iloc[:, ds.col_idx].std()

    def observation(self, idx: int) -> List[float]:
        obs = self.ds.observation(idx)
        obs = list(map(lambda x: (x - self.col_mean) / self.col_std, obs))
        return obs
