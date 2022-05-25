from typing import Optional

import numpy as np

from ml4trade.battery import Battery, EnergyBalance
from ml4trade.production import ProductionSystem
from ml4trade.consumption import ConsumptionSystem
from ml4trade.market import EnergyMarket
from ml4trade.wallet import Wallet
from ml4trade.units import Currency, MWh
from ml4trade.clock import ClockView


class Prosumer:
    def __init__(
            self,
            battery: Battery,
            production_system: ProductionSystem,
            consumption_system: ConsumptionSystem,
            clock_view: ClockView,
            initial_balance: Currency = Currency(0),
            energy_market: Optional[EnergyMarket] = None,
    ):
        self.battery = battery
        self.production_system = production_system
        self.consumption_system = consumption_system
        self.clock_view = clock_view
        self.wallet = Wallet(initial_balance)
        self.energy_market = energy_market
        self.energy_balance = EnergyBalance()

        self.scheduled_buy_amounts: Optional[np.ndarray] = None
        self.scheduled_sell_amounts: Optional[np.ndarray] = None
        self.scheduled_buy_thresholds: Optional[np.ndarray] = None
        self.scheduled_sell_thresholds: Optional[np.ndarray] = None
        self.next_day_actions: Optional[np.ndarray] = None

        self.last_scheduled_buy_transaction = None
        self.last_unscheduled_buy_transaction = None
        self.last_scheduled_sell_transaction = None
        self.last_unscheduled_sell_transaction = None

    def schedule(self, actions: np.ndarray):
        self.next_day_actions = actions

    def set_new_actions(self):
        self.scheduled_buy_amounts = [MWh(a) for a in self.next_day_actions[0:24]]
        self.scheduled_sell_amounts = [MWh(a) for a in self.next_day_actions[24:48]]
        self.scheduled_buy_thresholds = [Currency(a) for a in self.next_day_actions[48:72]]
        self.scheduled_sell_thresholds = [Currency(a) for a in self.next_day_actions[72:96]]
        self.next_day_actions = None

    def consume(self):
        self._consume_energy()
        cur_hour = self.clock_view.cur_datetime().time().hour
        self.buy_energy(
            self.scheduled_buy_amounts[cur_hour],
            self.scheduled_buy_thresholds[cur_hour],
        )
        self._restore_energy_balance()

    def produce(self):
        self._produce_energy()
        cur_hour = self.clock_view.cur_datetime().time().hour
        self.sell_energy(
            self.scheduled_sell_amounts[cur_hour],
            self.scheduled_sell_thresholds[cur_hour],
        )
        self._restore_energy_balance()

    def _consume_energy(self):
        self.energy_balance.sub(self.consumption_system.calculate_energy())

    def _produce_energy(self):
        self.energy_balance.add(self.production_system.calculate_energy())

    def buy_energy(self, amount: MWh, price: Currency, scheduled: bool = True):
        succeeded = self.energy_market.buy(amount, price, self.wallet, self.energy_balance, scheduled=scheduled)
        if scheduled:
            self.last_scheduled_buy_transaction = (amount.value, succeeded)
        else:
            self.last_unscheduled_buy_transaction = (amount.value, True)

    def sell_energy(self, amount: MWh, price: Currency, scheduled: bool = True):
        succeeded = self.energy_market.sell(amount, price, self.wallet, self.energy_balance, scheduled=scheduled)
        if scheduled:
            self.last_scheduled_sell_transaction = (amount.value, succeeded)
        else:
            self.last_unscheduled_sell_transaction = (amount.value, True)

    def _restore_energy_balance(self):
        if self.energy_balance.value < MWh(0):
            energy_used = self.battery.discharge(abs(self.energy_balance.value))
            self.energy_balance.value += energy_used
        elif self.energy_balance.value > MWh(0):
            energy_used = self.battery.charge(self.energy_balance.value)
            self.energy_balance.value -= energy_used

        if self.energy_balance.value > MWh(0):
            self.sell_energy(
                self.energy_balance.value,
                Currency(float('inf')),
                scheduled=False,
            )
        elif self.energy_balance.value < MWh(0):
            self.buy_energy(
                abs(self.energy_balance.value),
                Currency(float('0')),
                scheduled=False,
            )
