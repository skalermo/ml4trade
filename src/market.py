from typing import Tuple

import numpy as np
from pandas import DataFrame
from gym_anytrading.envs import TradingEnv

from src.custom_types import kWh, Currency
from src.wallet import Wallet
from src.battery import EnergyBalance


class EnergyMarket(TradingEnv):
    price_column = 'Fixing I Price [PLN/MWh]'

    def __init__(self, df: DataFrame = None, window_size: int = 0, frame_bound: Tuple[int, int] = None):
        if frame_bound is None:
            frame_bound = (window_size, len(df))
        self.frame_bound = frame_bound
        super().__init__(df, window_size)

        self.buy_price = 0
        self.buy_price_forced = 0
        self.sell_price = 0
        self.sell_price_forced = 0

    def _process_data(self) -> Tuple[DataFrame, np.ndarray]:
        prices = self.df.loc[:, self.price_column].to_numpy()
        assert len(prices) >= self.frame_bound[1] - (self.frame_bound[0] - self.window_size)

        prices = prices[self.frame_bound[0] - self.window_size:self.frame_bound[1]]

        diff = np.insert(np.diff(prices), 0, 0)
        signal_features = np.column_stack((prices, diff))

        return prices, signal_features

    def _calculate_reward(self, action):
        pass

    def buy(self, amount: kWh, price_threshold: Currency,
            client_wallet: Wallet, energy_balance: EnergyBalance,
            forced: bool = False):
        # if not forced client buys `amount` of energy at buy price not higher than `price_threshold`
        if not forced and self.buy_price > price_threshold:
            return
        energy_balance.add(amount)
        buy_price = self.buy_price if not forced else self.buy_price_forced
        client_wallet.withdraw(amount.to_cost(buy_price))

    def sell(self, amount: kWh, price_threshold: Currency,
             client_wallet: Wallet, energy_balance: EnergyBalance,
             forced: bool = False):
        # if not forced client sells `amount` of energy
        # at sell price not lower than `price_threshold`
        if not forced and self.sell_price < price_threshold:
            return
        energy_balance.sub(amount)
        sell_price = self.sell_price if not forced else self.sell_price_forced
        client_wallet.deposit(amount.to_cost(sell_price))

    def _update_profit(self, action):
        raise NotImplementedError

    def max_possible_profit(self):
        raise NotImplementedError

