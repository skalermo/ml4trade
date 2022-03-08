from custom_types import kWh, Currency


class EnergyMarket:
    def __init__(self, buy_price, sell_price):
        self.buy_price = buy_price
        self.sell_price = sell_price

    def buy(self, amount: kWh, price_threshold: Currency) -> Currency:
        # consumer buys `amount` of energy at buy price not higher than `price_threshold`
        if self.buy_price <= price_threshold:
            return amount.to_cost(self.buy_price)
        return Currency(0.0)

    def sell(self, amount: kWh, price_threshold: Currency) -> Currency:
        # consumer sells `amount` of energy at sell price not lower than `price_threshold`
        if self.buy_price >= price_threshold:
            return amount.to_cost(self.buy_price)
        return Currency(0.0)
