from typing import Tuple, Dict, Union
from datetime import timedelta, datetime

import gym
from gym.core import Wrapper, ActionWrapper as _ActionWrapper
import pandas as pd
import numpy as np

from ml4trade.simulation_env import SimulationEnv


CUSTOM_ACTION_SPACE = gym.spaces.Box(
    low=np.array([-10] * 96),
    high=np.array([10] * 96),
)


class ActionWrapper(_ActionWrapper):
    env: SimulationEnv

    def __init__(self, env: Union[SimulationEnv, Wrapper], ref_power_MW: float,
                 avg_month_price_retriever: 'AvgMonthPriceRetriever'):
        super().__init__(env)
        self.env.action_space = CUSTOM_ACTION_SPACE
        self._ref_power_MW = ref_power_MW
        self._avg_month_price_retriever = avg_month_price_retriever
        self._clock_view = self.env.new_clock_view()

    def action(self, action):
        new_action = np.exp(action)
        new_action[:48] *= self.ref_power_MW / 2
        price = self.avg_month_price_retriever.get_prev_month_avg_price(
            self._clock_view.cur_datetime()
        )
        new_action[48:] *= price
        return new_action

    def reverse_action(self, action):
        raise NotImplementedError


class AvgMonthPriceRetriever:
    def __init__(self, prices_df: pd.DataFrame):
        self._avg_month_prices: Dict[Tuple[int, int], float] = prices_df.groupby(
            [prices_df['index'].dt.year.rename('year'), prices_df['index'].dt.month.rename('month')]
        )['Fixing I Price [PLN/MWh]'].mean().to_dict()
        self._default_avg_price = list(self._avg_month_prices.values())[0]

    def get_prev_month_avg_price(self, _datetime: datetime) -> float:
        prev_month = self._get_prev_month(_datetime)
        prev_month_avg_price = self._avg_month_prices.get(prev_month, self._default_avg_price)
        return prev_month_avg_price

    def _get_prev_month(self, _datetime: datetime) -> Tuple[int, int]:
        prev_month_datetime = _datetime.replace(day=1) - timedelta(days=1)
        return prev_month_datetime.year, prev_month_datetime.month
