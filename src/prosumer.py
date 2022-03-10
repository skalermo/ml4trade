from typing import Optional
from datetime import datetime, time

import numpy as np

from src.battery import Battery
from src.energy_manipulation.energy_systems import EnergySystems
from src.market import EnergyMarket
from src.wallet import Wallet
from src.custom_types import Currency, kWh


SELL_THRESHOLD = Currency(0.5)


class Prosumer:
    def __init__(
            self,
            battery: Battery,
            energy_systems: EnergySystems,
            initial_balance: Currency = Currency(0),
            energy_market: Optional[EnergyMarket] = None,
    ):
        self.battery = battery
        self.energy_systems = energy_systems
        self.wallet = Wallet(initial_balance)
        self.hourly_energy_balance = 0
        self.energy_market = energy_market
        self.scheduled_trading_amounts: Optional[np.ndarray] = None
        self.scheduled_price_thresholds: Optional[np.ndarray] = None
        self.next_day_actions: Optional[np.ndarray] = None

    def consume_energy(self):
        pass

    def _produce_energy(self, _) -> kWh:
        power_produced = self.energy_systems.get_production_power(0)
        return power_produced.to_kwh()

    def _sell_energy(self, amount: kWh, _):
        self.energy_market.sell(amount, SELL_THRESHOLD, self.wallet, self.battery)

    def produce_and_sell(self, _datetime: datetime):
        energy_produced = self._produce_energy(_datetime)
        self._sell_energy(energy_produced, _datetime)

    def schedule(self, actions: np.ndarray):
        self.next_day_actions = actions

    def set_new_actions(self) -> bool:
        if self.next_day_actions is None:
            return False
        self.scheduled_trading_amounts = self.next_day_actions[0:24]
        self.scheduled_price_thresholds = self.next_day_actions[24:]
        self.next_day_actions = None
        return True

    def get_scheduled_buy_amount(self, _time: time) -> kWh:
        if self.scheduled_trading_amounts is None:
            return kWh(0)
        scheduled_amount = self.scheduled_trading_amounts[_time.hour]
        if scheduled_amount <= 0:
            return kWh(0)
        return kWh(scheduled_amount)

    def get_scheduled_sell_amount(self, _time: time) -> kWh:
        if self.scheduled_trading_amounts is None:
            return kWh(0)
        scheduled_amount = self.scheduled_trading_amounts[_time.hour]
        if scheduled_amount >= 0:
            return kWh(0)
        return kWh(scheduled_amount)

    def get_scheduled_price_threshold(self, _time: time) -> Currency:
        if self.scheduled_price_thresholds is None:
            return Currency(0)
        return Currency(self.scheduled_price_thresholds[_time.hour])
