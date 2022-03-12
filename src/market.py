from src.custom_types import kWh, Currency
from src.wallet import Wallet
from src.battery import EnergyBalance


class EnergyMarket:
    def __init__(self, buy_price: Currency, sell_price: Currency):
        self.buy_price = buy_price
        self.buy_price_forced = buy_price * 1.1
        self.sell_price = sell_price
        self.sell_price_forced = sell_price / 1.1

    def buy(self, amount: kWh, price_threshold: Currency, client_wallet: Wallet, energy_balance: EnergyBalance, forced: bool = False):
        # client buys `amount` of energy at buy price not higher than `price_threshold`
        if self.buy_price <= price_threshold:
            energy_balance.add(amount)
            client_wallet.withdraw(amount.to_cost(self.buy_price))

    def sell(self, amount: kWh, price_threshold: Currency, client_wallet: Wallet, energy_balance: EnergyBalance, forced: bool = False):
        # client sells `amount` of energy at sell price not lower than `price_threshold`
        if self.sell_price >= price_threshold:
            energy_balance.sub(amount)
            client_wallet.deposit(amount.to_cost(self.sell_price))
