from typing import List

from src.units import MWh, Currency
from src.wallet import Wallet
from src.battery import EnergyBalance
from src.data_strategies.base import DataStrategy
from src.clock import ClockView


UNSCHEDULED_MULTIPLIER = 2.0


class EnergyMarket:
    def __init__(self, ds: DataStrategy, clock_view: ClockView, window_size: int = 24):
        self.ds = ds
        self.clock_view = clock_view
        self.window_size = window_size

    def buy(self, amount: MWh, price_threshold: Currency,
            client_wallet: Wallet, energy_balance: EnergyBalance,
            scheduled: bool = True) -> bool:
        # if scheduled client buys `amount` of energy at buy price not higher than `price_threshold`
        if scheduled and self.get_buy_price() > price_threshold:
            return False
        energy_balance.add(amount)
        buy_price = self.get_buy_price() if scheduled else self.get_buy_price_unscheduled()
        client_wallet.withdraw(amount.to_cost(buy_price))
        return True

    def sell(self, amount: MWh, price_threshold: Currency,
             client_wallet: Wallet, energy_balance: EnergyBalance,
             scheduled: bool = True) -> bool:
        # if scheduled client sells `amount` of energy
        # at sell price not lower than `price_threshold`
        if scheduled and self.get_sell_price() < price_threshold:
            return False
        energy_balance.sub(amount)
        sell_price = self.get_sell_price() if scheduled else self.get_sell_price_unscheduled()
        client_wallet.deposit(amount.to_cost(sell_price))
        return True

    def get_buy_price(self):
        return Currency(self.ds.process(self.clock_view.cur_tick()))

    def get_sell_price(self):
        return Currency(self.ds.process(self.clock_view.cur_tick()))

    def get_buy_price_unscheduled(self):
        return self.get_buy_price() * UNSCHEDULED_MULTIPLIER

    def get_sell_price_unscheduled(self):
        return self.get_sell_price() / UNSCHEDULED_MULTIPLIER

    def observation(self) -> List[float]:
        return self.ds.observation(self.clock_view.cur_tick())
