import unittest

from ml4trade.domain.wallet import Wallet
from ml4trade.domain.units import Currency


class TestWallet(unittest.TestCase):
    def test_deposit(self):
        wallet = Wallet(Currency(0))
        wallet.deposit(Currency(100))
        self.assertEqual(wallet.balance, Currency(100))

    def test_withdraw(self):
        wallet = Wallet(Currency(0))
        wallet.withdraw(Currency(100))
        self.assertEqual(wallet.balance, Currency(-100))


if __name__ == '__main__':
    unittest.main()
