from typing import Optional
from datetime import datetime

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
        self.energy_balance = EnergyBalance()

        self.scheduled_buy_amounts: Optional[np.ndarray] = None
        self.scheduled_sell_amounts: Optional[np.ndarray] = None
        self.scheduled_buy_thresholds: Optional[np.ndarray] = None
        self.scheduled_sell_thresholds: Optional[np.ndarray] = None
        self.next_day_actions: Optional[np.ndarray] = None

    def _consume_energy(self, _):
        power_produced = self.energy_systems.get_consumption_power(0)
        self.energy_balance.sub(power_produced.to_kwh())

    def buy_energy(self, amount: kWh, price: Currency, scheduled: bool = True):
        self.energy_market.buy(amount, price, self.wallet, self.energy_balance, scheduled=scheduled)

    def consume(self, _datetime: datetime):
        self._consume_energy(_datetime)
        self.buy_energy(
            self.scheduled_buy_amounts[_datetime.time().hour],
            self.scheduled_buy_thresholds[_datetime.time().hour],
        )
        self._restore_energy_balance()

    def _produce_energy(self, _):
        power_produced = self.energy_systems.get_production_power(0)
        self.energy_balance.add(power_produced.to_kwh())

    def sell_energy(self, amount: kWh, price: Currency, scheduled: bool = True):
        self.energy_market.sell(amount, price, self.wallet, self.energy_balance, scheduled=scheduled)

    def produce(self, _datetime: datetime):
        self._produce_energy(_datetime)
        self.sell_energy(
            self.scheduled_sell_amounts[_datetime.time().hour],
            self.scheduled_sell_thresholds[_datetime.time().hour],
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
                scheduled=False,
            )
        elif self.energy_balance.value < kWh(0):
            self.buy_energy(
                abs(self.energy_balance.value),
                Currency(float('0')),
                scheduled=False,
            )

    def schedule(self, actions: np.ndarray):
        self.next_day_actions = actions

    def set_new_actions(self):
        self.scheduled_buy_amounts = [kWh(a) for a in self.next_day_actions[0:24]]
        self.scheduled_sell_amounts = [kWh(a) for a in self.next_day_actions[24:48]]
        self.scheduled_buy_thresholds = [Currency(a) for a in self.next_day_actions[48:72]]
        self.scheduled_sell_thresholds = [Currency(a) for a in self.next_day_actions[72:96]]
        self.next_day_actions = None
