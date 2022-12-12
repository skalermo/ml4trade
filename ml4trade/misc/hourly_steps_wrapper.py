from typing import Union, Tuple, Optional, List, NamedTuple

import numpy as np
from gymnasium.utils import seeding
from gymnasium.core import Wrapper, ObsType
from gymnasium.spaces import Discrete, MultiDiscrete

from ml4trade.simulation_env import SimulationEnv
from ml4trade.domain.clock import ClockView
from ml4trade.domain.units import MWh, Currency


BIG_THRESHOLD = 99999


class LastDayInfo(NamedTuple):
    prices: List[float]
    min_price: float
    max_price: float
    energy_surpluses: List[float]


class HourlyStepsWrapper(Wrapper):
    clock_view: ClockView
    _env: SimulationEnv

    def __init__(self, env: Union[SimulationEnv, Wrapper], use_dense_rewards: bool = False):
        super().__init__(env)
        self._env = env.unwrapped_env()
        self.action_space = Discrete(21)
        self.observation_space = MultiDiscrete([10, self.action_space.n, 10, 24])
        self.clock_view = self.new_clock_view()
        self.current_hour = self.clock_view._clock.action_replacement_time.hour
        self.day_actions = None
        self.saved_state: Optional[tuple] = None
        self.last_action: Optional[int] = None
        self.last_wallet_balance: Optional[float] = 0
        self.use_dense_rewards = use_dense_rewards
        # concerns time range 10:00-10:00
        self.last_day_info: Optional[LastDayInfo] = None
        self._rng, _ = seeding.np_random()

    def _convert_to_original_action_space(self, day_actions: np.ndarray) -> np.ndarray:
        converted_actions = [self._convert_to_original_action(a) for a in day_actions]
        res = np.array([a for tup in zip(*converted_actions) for a in tup])
        return res

    def _convert_to_original_action(self, a: int) -> (float, float, float, float):
        battery_cap = self._env._prosumer.battery.capacity.value
        if a == 0:
            return 0, 0, 0, 0
        if 1 <= a <= 10:  # discretized buy amounts
            return a / 10 * battery_cap , 0, BIG_THRESHOLD, BIG_THRESHOLD
        if 11 <= a <= 20:  # discretized sell amounts
            return 0, (a - 10) / 10 * battery_cap, 0, 0

    def reset(self, **kwargs) -> Tuple[ObsType, dict]:
        super(HourlyStepsWrapper, self).reset(**kwargs)
        # self.current_hour = self.clock_view.cur_datetime().hour
        self.current_hour = self.clock_view._clock.action_replacement_time.hour
        self.day_actions = None
        self.last_action = None
        self.last_wallet_balance = None
        self.last_day_info = None
        self._save_env_state()
        for _ in range(14):
            self._env._clock.tick()
        return self._observation(), {}

    def _save_env_state(self):
        scheduled_buy_amounts = None
        if self._env._prosumer.scheduled_buy_amounts is not None:
            scheduled_buy_amounts = self._env._prosumer.scheduled_buy_amounts[:]
        scheduled_sell_amounts = None
        if self._env._prosumer.scheduled_sell_amounts is not None:
            scheduled_sell_amounts = self._env._prosumer.scheduled_sell_amounts[:]
        scheduled_buy_thresholds = None
        if self._env._prosumer.scheduled_buy_thresholds is not None:
            scheduled_buy_thresholds = self._env._prosumer.scheduled_buy_thresholds[:]
        scheduled_sell_thresholds = None
        if self._env._prosumer.scheduled_sell_thresholds is not None:
            scheduled_sell_thresholds = self._env._prosumer.scheduled_sell_thresholds[:]

        self.saved_state = (
            self._env._prosumer.wallet.balance,
            self._env._prosumer.battery.current_charge,
            self._env._clock.cur_datetime,
            self._env._clock.cur_tick,
            scheduled_buy_amounts,
            scheduled_sell_amounts,
            scheduled_buy_thresholds,
            scheduled_sell_thresholds,
            self._rng.bit_generator.state,
        )

    def _restore_env_state(self):
        if self.saved_state is not None:
            (
                self._env._prosumer.wallet.balance,
                self._env._prosumer.battery.current_charge,
                self._env._clock.cur_datetime,
                self._env._clock.cur_tick,
                self._env._prosumer.scheduled_buy_amounts,
                self._env._prosumer.scheduled_sell_amounts,
                self._env._prosumer.scheduled_buy_thresholds,
                self._env._prosumer.scheduled_sell_thresholds,
                self._rng.bit_generator.state,
            ) = self.saved_state

    def _set_cur_prosumer_action(self, a: int):
        (
            buy_amount,
            sell_amount,
            buy_threshold,
            sell_threshold,
        ) = self._convert_to_original_action(a)
        if self._env._prosumer.scheduled_buy_amounts is None:
            self._env._prosumer.scheduled_buy_amounts = [0] * 24
        if self._env._prosumer.scheduled_sell_amounts is None:
            self._env._prosumer.scheduled_sell_amounts = [0] * 24
        if self._env._prosumer.scheduled_buy_thresholds is None:
            self._env._prosumer.scheduled_buy_thresholds = [0] * 24
        if self._env._prosumer.scheduled_sell_thresholds is None:
            self._env._prosumer.scheduled_sell_thresholds = [0] * 24
        self._env._prosumer.scheduled_buy_amounts[self.current_hour] = MWh(buy_amount)
        self._env._prosumer.scheduled_sell_amounts[self.current_hour] = MWh(sell_amount)
        self._env._prosumer.scheduled_buy_thresholds[self.current_hour] = Currency(buy_threshold)
        self._env._prosumer.scheduled_sell_thresholds[self.current_hour] = Currency(sell_threshold)

    def step(self, action: int) -> Tuple[ObsType, float, bool, bool, dict]:
        reward = 0
        terminated = False
        truncated = False

        if self.current_hour == 0 and self.day_actions is not None:
            self._restore_env_state()
            _, reward, terminated, truncated, _ = super().step(self._convert_to_original_action_space(self.day_actions))
            self._save_env_state()
            self._update_last_day_info()
            self.day_actions = np.zeros(24)
            if not truncated:
                for _ in range(14):
                    self._env._rand_produce_consume()
                    self._env._clock.tick()
        if self.day_actions is None:
            self.day_actions = np.zeros(24)

        self.last_action = action
        self.day_actions[self.current_hour] = action

        if not truncated:
            # perform 1-hour step
            self._set_cur_prosumer_action(action)
            self._env._rand_produce_consume()
            self._env._clock.tick()
            self.current_hour = (self.current_hour + 1) % 24

        if self.use_dense_rewards:
            reward = self._reward()
        self.last_wallet_balance = self._env._prosumer.wallet.balance.value
        return self._observation(), reward, terminated, truncated, {}

    def _update_last_day_info(self):
        history = self._env.history
        end_idx = history._cur_tick_to_idx()
        start_idx = end_idx - 24 or None
        last_day_history = history._history[start_idx:end_idx]
        last_day_prices = list(map(lambda x: x['price'], last_day_history))
        energy_surpluses = list(r['energy_produced'] - r['energy_consumed'] for r in last_day_history)
        if all(last_day_prices):
            self.last_day_info = LastDayInfo(
                prices=last_day_prices,
                min_price=min(last_day_prices),
                max_price=max(last_day_prices),
                energy_surpluses=energy_surpluses,
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
        reward = self._env._prosumer.wallet.balance.value - (self.last_wallet_balance or 0)
        if self.last_day_info is not None:
            reward -= self.last_day_info.energy_surpluses[self.current_hour] * self.last_day_info.prices[self.current_hour]
        return reward
