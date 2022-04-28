from typing import List

from pandas import DataFrame

from src.custom_types import kWh, Currency
from src.wallet import Wallet
from src.battery import EnergyBalance
from src.callback import Callback
from src.clock import ClockView


UNSCHEDULED_MULTIPLIER = 2.0


class EnergyMarket:
    def __init__(self, df: DataFrame, cb: Callback, clock_view: ClockView, window_size: int = 24):
        self.df = df
        self.cb = cb
        self.clock_view = clock_view
        self.window_size = window_size

    def buy(self, amount: kWh, price_threshold: Currency,
            client_wallet: Wallet, energy_balance: EnergyBalance,
            scheduled: bool = True):
        # if scheduled client buys `amount` of energy at buy price not higher than `price_threshold`
        if scheduled and self.get_buy_price() > price_threshold:
            return
        energy_balance.add(amount)
        buy_price = self.get_buy_price() if scheduled else self.get_buy_price_unscheduled()
        client_wallet.withdraw(amount.to_cost(buy_price))

    def sell(self, amount: kWh, price_threshold: Currency,
             client_wallet: Wallet, energy_balance: EnergyBalance,
             scheduled: bool = True):
        # if scheduled client sells `amount` of energy
        # at sell price not lower than `price_threshold`
        if scheduled and self.get_sell_price() < price_threshold:
            return
        energy_balance.sub(amount)
        sell_price = self.get_sell_price() if scheduled else self.get_sell_price_unscheduled()
        client_wallet.deposit(amount.to_cost(sell_price))

    def get_buy_price(self):
        return self.cb.process(self.df, self.clock_view.cur_tick())

    def get_sell_price(self):
        return self.cb.process(self.df, self.clock_view.cur_tick())

    def get_buy_price_unscheduled(self):
        return self.get_buy_price() * UNSCHEDULED_MULTIPLIER

    def get_sell_price_unscheduled(self):
        return self.get_sell_price() / UNSCHEDULED_MULTIPLIER

    def observation(self) -> List[float]:
        cur_tick = self.clock_view.cur_tick()
        res = [self.cb.process(self.df, tick).value for tick in range(cur_tick - self.window_size + 1, cur_tick + 1)]
        return res
