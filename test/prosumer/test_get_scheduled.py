import unittest
from datetime import time

from src.simulation_env import SimulationEnv
from src.custom_types import kWh, Currency

from utils import setup_default_market


class GetScheduledBuyAmount(unittest.TestCase):
    def setUp(self):
        self.env = SimulationEnv()
        self.env.prosumer.energy_market = setup_default_market()

    def test_if_none_returns_zero(self):
        amount = self.env.prosumer.get_scheduled_buy_amount(time(0, 0))
        self.assertEqual(amount, kWh(0))

    def test_returns_scheduled_value(self):
        action = self.env.action_space.sample()
        self.env.step(action)
        amount = self.env.prosumer.get_scheduled_buy_amount(time(0, 0))
        self.assertEqual(amount, kWh(action[0]))

    def test_cant_have_negative_value(self):
        action = self.env.action_space.sample()
        action[0] = -1
        self.env.prosumer.scheduled_trading_amounts = action[:48]
        with self.assertRaises(AssertionError):
            self.env.prosumer.get_scheduled_buy_amount(time(0, 0))


class GetScheduledSellAmount(unittest.TestCase):
    def setUp(self):
        self.env = SimulationEnv()
        self.env.prosumer.energy_market = setup_default_market()

    def test_if_none_returns_zero(self):
        amount = self.env.prosumer.get_scheduled_sell_amount(time(0, 0))
        self.assertEqual(amount, kWh(0))

    def test_returns_scheduled_value(self):
        action = self.env.action_space.sample()
        self.env.step(action)
        amount = self.env.prosumer.get_scheduled_sell_amount(time(0, 0))
        self.assertEqual(amount, kWh(action[24 + 0]))

    def test_cant_have_negative_value(self):
        action = self.env.action_space.sample()
        action[24 + 0] = -1
        self.env.prosumer.scheduled_trading_amounts = action[:48]
        with self.assertRaises(AssertionError):
            self.env.prosumer.get_scheduled_sell_amount(time(0, 0))


class GetScheduledBuyPriceThreshold(unittest.TestCase):
    def setUp(self):
        self.env = SimulationEnv()
        self.env.prosumer.energy_market = setup_default_market()

    def test_if_none_returns_zero(self):
        amount = self.env.prosumer.get_scheduled_buy_price_threshold(time(0, 0))
        self.assertEqual(amount, Currency(0))

    def test_returns_scheduled_value(self):
        action = self.env.action_space.sample()
        self.env.step(action)
        amount = self.env.prosumer.get_scheduled_buy_price_threshold(time(0, 0))
        self.assertEqual(amount, Currency(action[48 + 0]))

    def test_cant_have_negative_value(self):
        action = self.env.action_space.sample()
        action[48 + 0] = -1
        self.env.prosumer.scheduled_price_thresholds = action[48:]
        with self.assertRaises(AssertionError):
            self.env.prosumer.get_scheduled_buy_price_threshold(time(0, 0))


class GetScheduledSellPriceThreshold(unittest.TestCase):
    def setUp(self):
        self.env = SimulationEnv()
        self.env.prosumer.energy_market = setup_default_market()

    def test_if_none_returns_zero(self):
        amount = self.env.prosumer.get_scheduled_sell_price_threshold(time(0, 0))
        self.assertEqual(amount, Currency(0))

    def test_returns_scheduled_value(self):
        action = self.env.action_space.sample()
        self.env.step(action)
        amount = self.env.prosumer.get_scheduled_sell_price_threshold(time(0, 0))
        self.assertEqual(amount, Currency(action[48 + 24 + 0]))

    def test_cant_have_negative_value(self):
        action = self.env.action_space.sample()
        action[48 + 24 + 0] = -1
        self.env.prosumer.scheduled_price_thresholds = action[48:]
        with self.assertRaises(AssertionError):
            self.env.prosumer.get_scheduled_sell_price_threshold(time(0, 0))


if __name__ == '__main__':
    unittest.main()
