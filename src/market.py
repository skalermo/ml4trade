from pandas import DataFrame

from src.custom_types import kWh, Currency
from src.wallet import Wallet
from src.battery import EnergyBalance
from src.callback import Callback
from src.clock import ClockView


FORCED_MULTIPLIER = 2.0


class EnergyMarket:
    def __init__(self, df: DataFrame, cb: Callback, clock_view: ClockView):
        self.df = df
        self.cb = cb
        self.clock_view = clock_view

    def buy(self, amount: kWh, price_threshold: Currency,
            client_wallet: Wallet, energy_balance: EnergyBalance,
            forced: bool = False):
        # if not forced client buys `amount` of energy at buy price not higher than `price_threshold`
        if not forced and self.get_buy_price() > price_threshold:
            return
        energy_balance.add(amount)
        buy_price = self.get_buy_price() if not forced else self.get_buy_price_forced()
        client_wallet.withdraw(amount.to_cost(buy_price))

    def sell(self, amount: kWh, price_threshold: Currency,
             client_wallet: Wallet, energy_balance: EnergyBalance,
             forced: bool = False):
        # if not forced client sells `amount` of energy
        # at sell price not lower than `price_threshold`
        if not forced and self.get_sell_price() < price_threshold:
            return
        energy_balance.sub(amount)
        sell_price = self.get_sell_price() if not forced else self.get_sell_price_forced()
        client_wallet.deposit(amount.to_cost(sell_price))

    def get_buy_price(self):
        return self.cb.process(self.df, self.clock_view.cur_tick())

    def get_sell_price(self):
        return self.cb.process(self.df, self.clock_view.cur_tick())

    def get_buy_price_forced(self):
        return self.get_buy_price() * FORCED_MULTIPLIER

    def get_sell_price_forced(self):
        return self.get_sell_price() / FORCED_MULTIPLIER
