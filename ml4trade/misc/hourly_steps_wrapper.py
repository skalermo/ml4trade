from typing import Union, Tuple, Optional, List, NamedTuple

import numpy as np
from gymnasium.core import Wrapper, ObsType
from gymnasium.spaces import Discrete, MultiDiscrete

from ml4trade.simulation_env import SimulationEnv
from ml4trade.domain.clock import ClockView


BIG_THRESHOLD = 99999


class LastDayInfo(NamedTuple):
    prices: List[float]
    min_price: float
    max_price: float
    sparse_reward: float


class HourlyStepsWrapper(Wrapper):
    clock_view: ClockView
    _env: SimulationEnv

    def __init__(self, env: Union[SimulationEnv, Wrapper], use_dense_rewards: bool = False):
        super().__init__(env)
        self._env = env.unwrapped_env()
        self.action_space = Discrete(21)
        self.observation_space = MultiDiscrete([10, self.action_space.n, 10, 24])
        self.clock_view = self.new_clock_view()
        self.current_hour = self.clock_view.cur_datetime().hour
        self.day_actions = np.zeros(24)
        self.saved_state: Optional[tuple] = None
        self.last_action: Optional[int] = None
        self.last_wallet_balance: Optional[float] = 0
        self.use_dense_rewards = use_dense_rewards
        # concerns time range 10:00-10:00
        self.last_day_info: Optional[LastDayInfo] = None

    def _convert_to_original_action_space(self, day_actions: np.ndarray):
        res = np.zeros(96)
        for i, a in enumerate(day_actions):
            if a == 0:
                res[i] = 0
                res[i + 24] = 0
                res[i + 48] = 0
                res[i + 72] = 0
            elif 1 <= a <= 10:  # discretized buy amounts
                res[i] = a / 10
                res[i + 24] = 0
                res[i + 48] = BIG_THRESHOLD  # guaranteed to buy
                res[i + 72] = BIG_THRESHOLD  # guaranteed to not sell
            elif 11 <= a <= 20:  # discretized sell amounts
                res[i] = 0
                res[i + 24] = (a - 10) / 10
                res[i + 48] = 0  # guaranteed to not buy
                res[i + 72] = 0  # guaranteed to sell
        return res

    def reset(self, **kwargs) -> Tuple[ObsType, dict]:
        super(HourlyStepsWrapper, self).reset(**kwargs)
        self.current_hour = self.clock_view.cur_datetime().hour
        self.saved_state = None
        self.last_action = None
        self.last_wallet_balance = None
        self.last_day_info = None
        return self._observation(), {}

    def step(self, action: int) -> Tuple[ObsType, float, bool, bool, dict]:
        self.last_action = action
        self.day_actions[self.current_hour] = action
        reward = 0
        terminated = False
        truncated = False
        if self.current_hour == self.clock_view.scheduling_hour():
            if self.saved_state is not None:
                (
                    self._env._prosumer.wallet.balance,
                    self._env._prosumer.battery.current_charge,
                    self._env._clock.cur_datetime,
                    self._env._clock.cur_tick,
                ) = self.saved_state
            _, reward, terminated, truncated, _ = super().step(
                self._convert_to_original_action_space(self.day_actions)
            )
            self.saved_state = (
                self._env._prosumer.wallet.balance,
                self._env._prosumer.battery.current_charge,
                self._env._clock.cur_datetime,
                self._env._clock.cur_tick,
            )
            self._update_last_day_info(reward)
            self.day_actions = np.zeros(24)
        if self._env._first_actions_set:
            self._env._rand_produce_consume()
        if not truncated:
            self._env._clock.tick()
        self.current_hour = (self.current_hour + 1) % 24
        if self.use_dense_rewards:
            reward = self._reward()
        self.last_wallet_balance = self._env._prosumer.wallet.balance.value
        return self._observation(), reward, terminated, truncated, {}

    def _update_last_day_info(self, sparse_reward: float):
        history = self._env.history
        end_idx = history._cur_tick_to_idx()
        start_idx = end_idx - 24 or None
        last_day_prices = list(map(lambda x: x['price'], history._history[start_idx:end_idx]))
        if all(last_day_prices):
            self.last_day_info = LastDayInfo(
                prices=last_day_prices,
                min_price=min(last_day_prices),
                max_price=max(last_day_prices),
                sparse_reward=sparse_reward,
            )

    def _last_day_discretized_price(self, t: int) -> int:
        if self.last_day_info is None:
            return 5
        price_at_t = self.last_day_info.prices[(t - 10 + 24) % 24]
        price_after_conversion = np.interp(
            price_at_t,
            [self.last_day_info.min_price, self.last_day_info.max_price],
            [0, 10],
        )
        discretized_price = min(int(price_after_conversion), 9)
        return discretized_price

    def _observation(self) -> np.ndarray:
        predicted_rel_battery_charge = self._env._prosumer.battery.rel_current_charge
        discretized_battery_charge = min(int(predicted_rel_battery_charge * 10), 9)
        discretized_price = self._last_day_discretized_price(self.current_hour)
        obs = np.array([discretized_price, self.last_action or 0, discretized_battery_charge, self.current_hour])
        return obs

    def _reward(self) -> float:
        reward = self._env._prosumer.wallet.balance.value - (self.last_wallet_balance or 0)\
                 + self.last_day_info.sparse_reward / 24
        return reward
