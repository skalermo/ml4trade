from ml4trade.domain.units import Currency


class Wallet:
    def __init__(self, initial_balance: Currency = Currency(0)):
        self.balance = initial_balance

    def deposit(self, amount: Currency):
        self.balance += amount

    def withdraw(self, amount: Currency):
        self.balance -= amount
