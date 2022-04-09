from typing import Optional, Union, Tuple, Generator, List, Any
from datetime import datetime, timedelta, time
import random

import numpy as np
import pandas as pd
import gym
from gym import spaces
from gym.core import ObsType, ActType

from src.custom_types import Currency
from src.prosumer import Prosumer
from src.battery import Battery
from src.energy_manipulation.energy_systems import EnergySystems
from src.market import EnergyMarket
from src.clock import SimulationClock
from src.constants import *


ObservationType = Tuple[ObsType, float, bool, dict]


class SimulationEnv(gym.Env):
    def __init__(
            self,
            start_datetime: datetime = START_TIME,
            scheduling_time: time = SCHEDULING_TIME,
            action_replacement_time: time = ACTION_REPLACEMENT_TIME,
            # prices_df: pd.DataFrame,
            market_buy_price: float = 1.0,
            market_sell_price: float = 1.0,
    ):
        self.action_space = SIMULATION_ENV_ACTION_SPACE
        self.shape = (1, 1)
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=self.shape, dtype=np.float32)

        self.scheduling_time = scheduling_time
        self.action_replacement_time = action_replacement_time
        self._clock = SimulationClock(
            start_datetime=start_datetime,
            scheduling_time=scheduling_time,
            action_replacement_time=action_replacement_time,
            start_tick=0,
            tick_duration=timedelta(hours=1)
        )

        self.simulation = self._simulation()
        self.first_actions_set = False

        battery = Battery()
        energy_systems = EnergySystems()
        self.energy_market = EnergyMarket(Currency(market_buy_price), Currency(market_sell_price))
        self.prosumer = Prosumer(battery, energy_systems, energy_market=self.energy_market)

        # start generator object
        self.simulation.send(None)

    def reset(self, *, seed: Optional[int] = None, return_info: bool = False, options: Optional[dict] = None) -> Union[
        ObsType, Tuple[ObsType, dict]]:
        return np.zeros(self.shape)

    def _observation(self) -> ObservationType:
        return np.zeros(self.shape), 0, False, {}

    def step(self, action: ActType) -> ObservationType:
        return self.simulation.send(action)

    def _simulation(self) -> Generator[ObservationType, ActType, None]:
        while True:
            if self._clock.is_it_scheduling_hour():
                action = yield self._observation()
                self.prosumer.schedule(action)

            if self._clock.is_it_action_replacement_hour():
                are_actions_set = self.prosumer.set_new_actions()
                if are_actions_set and not self.first_actions_set:
                    self.first_actions_set = True

            if self.first_actions_set:
                self._run_in_random_order([
                    (self.prosumer.consume, [self._clock.cur_datetime]),
                    (self.prosumer.produce, [self._clock.cur_datetime]),
                ])

            self._clock.tick()

    @staticmethod
    def _run_in_random_order(functions_and_calldata: List[Tuple[callable, List[Any]]]) -> None:
        random.shuffle(functions_and_calldata)
        for f, args in functions_and_calldata:
            f(*args)

    def render(self, mode="human"):
        pass
