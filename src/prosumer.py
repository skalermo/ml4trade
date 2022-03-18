from typing import Optional
from datetime import datetime, time

import numpy as np

from src.battery import Battery, EnergyBalance
from src.energy_manipulation.energy_systems import EnergySystems
from src.market import EnergyMarket
from src.wallet import Wallet
from src.custom_types import Currency, kWh


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
        self.energy_balance = EnergyBalance()

    def _consume_energy(self, _) -> kWh:
        power_produced = self.energy_systems.get_consumption_power(0)
        return power_produced.to_kwh()

    def buy_energy(self, amount: kWh, price: Currency, forced: bool = False):
        self.energy_market.buy(amount, price, self.wallet, self.energy_balance, forced=forced)

    def consume_energy(self, amount: kWh):
        self.energy_balance.sub(amount)

    def consume(self, _datetime: datetime):
        energy_consumed = self._consume_energy(_datetime)
        self.consume_energy(energy_consumed)
        self.buy_energy(
            self.get_scheduled_buy_amount(_datetime.time()),
            self.get_scheduled_buy_price_threshold(_datetime.time()),
        )
        self._restore_energy_balance()

    def _produce_energy(self, _) -> kWh:
        power_produced = self.energy_systems.get_production_power(0)
        return power_produced.to_kwh()

    def sell_energy(self, amount: kWh, price: Currency, forced: bool = False):
        self.energy_market.sell(amount, price, self.wallet, self.energy_balance, forced=forced)

    def produce_energy(self, amount: kWh):
        self.energy_balance.add(amount)

    def produce(self, _datetime: datetime):
        energy_produced = self._produce_energy(_datetime)
        self.produce_energy(energy_produced)
        self.sell_energy(
            self.get_scheduled_sell_amount(_datetime.time()),
            self.get_scheduled_sell_price_threshold(_datetime.time()),
        )
        self._restore_energy_balance()

    def _restore_energy_balance(self):
        if self.energy_balance.value < kWh(0):
            energy_used = self.battery.discharge(abs(self.energy_balance.value))
            self.energy_balance.value += energy_used
        elif self.energy_balance.value > kWh(0):
            energy_used = self.battery.charge(self.energy_balance.value)
            self.energy_balance.value -= energy_used

        if self.energy_balance.value > kWh(0):
            self.sell_energy(
                self.energy_balance.value,
                Currency(float('inf')),
                forced=True,
            )
        elif self.energy_balance.value < kWh(0):
            self.buy_energy(
                abs(self.energy_balance.value),
                Currency(float('0')),
                forced=True,
            )

    def schedule(self, actions: np.ndarray):
        self.next_day_actions = actions

    def set_new_actions(self) -> bool:
        if self.next_day_actions is None:
            return False
        self.scheduled_trading_amounts = self.next_day_actions[0:48]
        self.scheduled_price_thresholds = self.next_day_actions[48:]
        self.next_day_actions = None
        return True

    def get_scheduled_buy_amount(self, _time: time) -> kWh:
        if self.scheduled_trading_amounts is None:
            return kWh(0)
        scheduled_amount = self.scheduled_trading_amounts[_time.hour]
        assert scheduled_amount >= 0

        return kWh(scheduled_amount)

    def get_scheduled_sell_amount(self, _time: time) -> kWh:
        if self.scheduled_trading_amounts is None:
            return kWh(0)
        scheduled_amount = self.scheduled_trading_amounts[24 + _time.hour]
        assert scheduled_amount >= 0

        return kWh(scheduled_amount)

    def get_scheduled_buy_price_threshold(self, _time: time) -> Currency:
        if self.scheduled_price_thresholds is None:
            return Currency(0)
        return Currency(self.scheduled_price_thresholds[_time.hour])

    def get_scheduled_sell_price_threshold(self, _time: time) -> Currency:
        if self.scheduled_price_thresholds is None:
            return Currency(0)
        return Currency(self.scheduled_price_thresholds[24 + _time.hour])
