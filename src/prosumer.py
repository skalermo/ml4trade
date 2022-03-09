from typing import Optional

import numpy as np

from src.battery import Battery
from src.energy_manipulation.energy_systems import EnergySystems
from src.market import EnergyMarket


class Prosumer:
    def __init__(
            self,
            battery: Battery,
            energy_systems: EnergySystems,
            balance: int = 0,
            energy_market: Optional[EnergyMarket] = None
    ):
        self.battery = battery
        self.energy_systems = energy_systems
        self.balance = balance
        self.energy_market = energy_market
        self.scheduled_trading_amounts: Optional[np.ndarray] = None
        self.scheduled_price_thresholds: Optional[np.ndarray] = None
        self.next_day_actions: Optional[np.ndarray] = None

    def consume_energy(self):
        pass

    def produce_energy(self):
        pass

    def sell_energy(self):
        pass

    def produce_and_sell(self):
        pass

    def schedule(self, actions: np.ndarray):
        self.next_day_actions = actions

    def set_new_actions(self):
        self.scheduled_trading_amounts = self.next_day_actions[0:24]
        self.scheduled_price_thresholds = self.next_day_actions[24:]
        self.next_day_actions = None

    def get_scheduled_buy_amount(self, hour: int):
        pass

    def get_scheduled_sell_amount(self, hour: int):
        pass
