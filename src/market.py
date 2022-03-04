class EnergyMarket:
    def __init__(self, buy_price, sell_price):
        self.buy_price = buy_price
        self.sell_price = sell_price

    def buy(self, amount, price_threshold) -> float:
        # consumer buys `amount` of energy at buy price not higher than `price_threshold`
        if self.buy_price <= price_threshold:
            return amount * self.buy_price
        return 0.0

    def sell(self, amount, price_threshold) -> float:
        # consumer sells `amount` of energy at sell price not lower than `price_threshold`
        if self.buy_price >= price_threshold:
            return amount * self.buy_price
        return 0.0
