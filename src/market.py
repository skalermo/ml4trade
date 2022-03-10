from src.custom_types import kWh, Currency
from src.wallet import Wallet
from src.battery import Battery


class EnergyMarket:
    def __init__(self, buy_price, sell_price):
        self.buy_price = buy_price
        self.sell_price = sell_price

    def buy(self, amount: kWh, price_threshold: Currency, client_wallet: Wallet, client_battery: Battery):
        # client buys `amount` of energy at buy price not higher than `price_threshold`
        if self.buy_price <= price_threshold:
            client_battery.charge(amount)
            client_wallet.withdraw(amount.to_cost(self.buy_price))

    def sell(self, amount: kWh, price_threshold: Currency, client_wallet: Wallet, client_battery: Battery):
        # client sells `amount` of energy at sell price not lower than `price_threshold`
        # battery must contain at least `amount` of energy if threshold allows for transaction
        if self.sell_price >= price_threshold:
            assert client_battery.current_charge >= amount
            client_battery.discharge(amount)
            client_wallet.deposit(amount.to_cost(self.sell_price))
