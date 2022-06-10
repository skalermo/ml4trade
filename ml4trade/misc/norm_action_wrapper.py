from typing import Tuple, Dict
from datetime import timedelta

from gym.core import Wrapper, ObsType, ActType
import numpy as np

from ml4trade.domain.clock import ClockView
from ml4trade.simulation_env import SimulationEnv


class CustomWrapper(Wrapper):
    env: SimulationEnv

    def __init__(self, env: SimulationEnv):
        super().__init__(env)

    def reset(self, **kwargs) -> ObsType:
        return super().reset(**kwargs)

    def step(self, action: ActType) -> Tuple[ObsType, float, bool, dict]:
        return super().step(action)

    def render_all(self):
        self.env.render_all()

    def save_history(self):
        self.env.save_history()


class ActionWrapper(CustomWrapper):
    def __init__(self, env: SimulationEnv, avg_month_prices: Dict[Tuple[int, int], float], ref_power_MW: float, clock_view: ClockView):
        super().__init__(env)
        self.avg_month_prices = avg_month_prices
        self.avg_prices = list(avg_month_prices.values())
        self.ref_power_MW = ref_power_MW
        self.clock_view = clock_view

    def step(self, action: ActType) -> Tuple[ObsType, float, bool, dict]:
        a = np.exp(action)
        a[:48] *= self.ref_power_MW / 2
        price = self._get_prev_month_avg_price()
        a[48:] *= price
        return super().step(a)

    def _get_prev_month_avg_price(self) -> float:
        prev_month_avg_price = self.avg_month_prices.get(self._get_prev_month(), self.avg_prices[0])
        return prev_month_avg_price

    def _get_prev_month(self) -> Tuple[int, int]:
        cur_datetime = self.clock_view.cur_datetime()
        prev_month_datetime = cur_datetime.replace(day=1) - timedelta(days=1)
        return prev_month_datetime.year, prev_month_datetime.month
