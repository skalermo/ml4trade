from typing import Optional
from datetime import datetime, time

import numpy as np

from src.battery import Battery, EnergyBalance
from src.energy_manipulation.energy_systems import EnergySystems
from src.market import EnergyMarket
from src.wallet import Wallet
from src.custom_types import Currency, kWh


SELL_THRESHOLD = Currency(0.5)
BUY_THRESHOLD = Currency(1.5)


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

    def consume(self, _datetime: datetime):
        consumption_power = self.energy_systems.get_consumption_power(_datetime.hour)
        bought_amount = self.get_scheduled_buy_amount(_datetime.time())
        self.energy_market.buy(bought_amount, BUY_THRESHOLD, self.wallet, self.energy_balance)
        consumed_amount = consumption_power.to_kwh()
        self.energy_balance.sub(consumed_amount)

        if self.energy_balance.value > kWh(0):
            pass

        # consumed_amount -= bought_amount
        # if consumed_amount.value > 0:
        #     discharged_amount = self.battery.discharge(consumed_amount)
        #     if discharged_amount < consumed_amount:
        #         needed_energy = consumed_amount - discharged_amount
        #         self.buy_energy(needed_energy, 1.2*self.get_scheduled_price(hour))
        # elif consumed_amount.value < 0:
        #     consumed_amount *= -1
        #     charged_amount = self.battery.charge(consumed_amount)
        #     deficient_amount = consumed_amount - charged_amount
        #     if deficient_amount.value > 0:
        #         self.sell_energy(deficient_amount, 0.8*self.get_scheduled_price(hour))

    def buy_energy(self, amount: kWh, price: Currency, forced: bool = False) -> float:
        return self.energy_market.buy(amount, price, self.wallet, self.energy_balance, forced=forced)

    def _produce_energy(self, _) -> kWh:
        power_produced = self.energy_systems.get_production_power(0)
        return power_produced.to_kwh()

    def sell_energy(self, amount: kWh, price: Currency, forced: bool = False):
        self.energy_market.sell(amount, price, self.wallet, self.energy_balance, forced=forced)

    def consume_energy(self, amount: kWh):
        pass

    def produce_energy(self, amount: kWh):
        self.energy_balance.add(amount)

    def _sell_energy(self, amount: kWh, _):
        pass
        # self.energy_market.sell(amount, SELL_THRESHOLD, self.wallet, self.battery)

    def produce(self, _datetime: datetime):
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
