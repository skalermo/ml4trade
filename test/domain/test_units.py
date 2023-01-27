from unittest import TestCase

from ml4trade.domain.units import MWh, Currency, MW


class TestMWh(TestCase):
    def setUp(self) -> None:
        self.mwh = MWh(1)

    def test_constructor(self):
        self.assertEqual(self.mwh, MWh(1))

    def test_to_cost(self):
        price = self.mwh.to_cost(Currency(2))
        self.assertEqual(price, Currency(2))

    def test__truediv(self):
        mwh1=self.mwh.__truediv__(MWh(2))
        self.assertEqual(mwh1, 0.5)
        mwh2=self.mwh.__truediv__(2)
        self.assertEqual(mwh2.value, 0.5)


class TestMW(TestCase):
    def setUp(self) -> None:
        self.mw = MW(1)

    def test_constructor(self):
        self.assertEqual(self.mw, MW(1))

    def test_to_mwh(self):
        self.assertEqual(self.mw.to_mwh(), MWh(1))

    def test__add__(self):
        mw1=self.mw.__add__(MW(1))
        self.assertEqual(mw1, MW(2))

    def test__sub__(self):
        mw1=self.mw.__sub__(MW(1))
        self.assertEqual(mw1, MW(0))


class TestCurrency(TestCase):
    def setUp(self) -> None:
        self.mw = MW(1)

    def test_constructor(self):
        self.assertEqual(self.mw, MW(1))
