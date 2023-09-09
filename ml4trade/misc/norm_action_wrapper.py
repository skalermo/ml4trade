from typing import Tuple, Dict, Union
from datetime import datetime

import gymnasium as gym
from gymnasium.core import Wrapper, ActionWrapper as _ActionWrapper
import pandas as pd
import numpy as np

from ml4trade.simulation_env import SimulationEnv


CUSTOM_ACTION_SPACE = gym.spaces.Box(
    low=np.array([-3] * 96),
    high=np.array([3] * 96),
)


class ActionWrapper(_ActionWrapper):
    env: SimulationEnv

    def __init__(self, env: Union[SimulationEnv, Wrapper], ref_power_MW: float,
                 avg_interval_price_retriever: 'AvgIntervalPriceRetriever'):
        super().__init__(env)
        self.env.action_space = CUSTOM_ACTION_SPACE
        self.ref_power_MW = ref_power_MW
        self.clock_view = self.env.new_clock_view()
        self._avg_interval_price_retriever = avg_interval_price_retriever

    def action(self, action):
        new_action = np.exp(action)
        new_action[:48] *= self.ref_power_MW / 2
        price = self._avg_interval_price_retriever.get_prev_interval_avg_price(
            self.clock_view.cur_datetime()
        )
        new_action[48:] *= price
        return new_action

    def reverse_action(self, action):
        raise NotImplementedError


class AvgIntervalPriceRetriever:
    def __init__(self, prices_df: pd.DataFrame, interval_days: int = 30):
        _avg_day_prices: Dict[Tuple[int, int], float] = prices_df.groupby(
            [
                prices_df['index'].dt.year.rename('year'),
                prices_df['index'].dt.month.rename('month'),
                prices_df['index'].dt.day.rename('day'),
            ],
        )['Fixing I Price [PLN/MWh]'].mean().to_dict()
        self._interval_days = interval_days
        self._dates = list(_avg_day_prices.keys())
        self._avg_prices = np.array(list(_avg_day_prices.values()))
        self._default_avg_price = np.average(self._avg_prices[0:interval_days])
        self._start_date = datetime(*self._dates[0])

    def get_prev_interval_avg_price(self, _datetime: datetime):
        cur_idx = (_datetime - self._start_date).days
        if cur_idx - self._interval_days <= 0:
            return self._default_avg_price
        return np.average(self._avg_prices[cur_idx - self._interval_days:cur_idx])
