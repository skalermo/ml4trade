from typing import Union, Tuple

import numpy as np
from gymnasium.core import Wrapper, ObsType
from gymnasium.spaces import Discrete, MultiDiscrete

from ml4trade.simulation_env import SimulationEnv
from ml4trade.domain.clock import ClockView


BIG_THRESHOLD = 99999


class HourlyStepsWrapper(Wrapper):
    clock_view: ClockView
    _env: SimulationEnv

    def __init__(self, env: Union[SimulationEnv, Wrapper]):
        super().__init__(env)
        self._env = env.unwrapped_env()
        self.action_space = Discrete(21)
        self.observation_space = MultiDiscrete([24, 11])
        self.clock_view = self.new_clock_view()
        self.current_hour = self.clock_view.cur_datetime().hour
        self.day_actions = np.zeros(24)
        self.saved_state = None

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
        return self._observation(), {}

    def step(self, action: int) -> Tuple[ObsType, float, bool, bool, dict]:
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
            self.day_actions = np.zeros(24)
        if self._env._first_actions_set:
            self._env._rand_produce_consume()
        if not truncated:
            self._env._clock.tick()
        self.current_hour = (self.current_hour + 1) % 24
        return self._observation(), reward, terminated, truncated, {}

    def _observation(self) -> np.ndarray:
        predicted_rel_battery_charge = self._env._prosumer.battery.rel_current_charge
        discretized_battery_charge = int(predicted_rel_battery_charge * 10)
        obs = np.array([self.current_hour, discretized_battery_charge])
        return obs
