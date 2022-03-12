import unittest
from datetime import datetime

from src.battery import Battery
from src.energy_manipulation.energy_systems import EnergySystems
from src.custom_types import kWh, Currency, kW
from src.market import EnergyMarket
from src.prosumer import Prosumer


class TestProsumer(unittest.TestCase):
    def test_init(self):
        battery = Battery(kWh(100), 1.0, kWh(50))
        energy_systems = EnergySystems()
        energy_market = EnergyMarket(Currency(0.5), Currency(1))
        prosumer = Prosumer(battery, energy_systems, Currency(50), energy_market)
        self.assertEqual(prosumer.battery.capacity, kWh(100))

    def test_consume_energy(self):
        battery = Battery(kWh(100), 1.0, kWh(50))
        energy_systems = EnergySystems()
        energy_market = EnergyMarket(Currency(0.5), Currency(1))
        prosumer = Prosumer(battery, energy_systems, Currency(50), energy_market)

        prosumer.consume_energy(kWh(10))

        self.assertEqual(prosumer.energy_balance, kWh(-10))

    def test_produce_energy(self):
        battery = Battery(kWh(100), 1.0, kWh(50))
        energy_systems = EnergySystems()
        energy_market = EnergyMarket(Currency(0.5), Currency(1))
        prosumer = Prosumer(battery, energy_systems, Currency(50), energy_market)

        prosumer.produce_energy(kWh(10))

        self.assertEqual(prosumer.energy_balance, kWh(10))

    # consume:
    # - buy
    # - consume (< buy)
    # - charged battery
    # - (sell forced)
    # - consume (> buy)
    # - discharge battery
    # - (buy forced)
    # produce:
    # - sell
    # - produce (> sell)
    # - charge battery
    # - (sell forced)
    # - produce (< sell)
    # - discharge battery
    # - (buy forced)


class TestProsumerBuy(unittest.TestCase):

    def test_buy(self):
        battery = Battery(kWh(100), 1.0, kWh(50))
        energy_systems = EnergySystems()
        energy_market = EnergyMarket(Currency(0.5), Currency(1))
        prosumer = Prosumer(battery, energy_systems, Currency(50), energy_market)

        prosumer.buy_energy(kWh(10), energy_market.buy_price)

        self.assertEqual(prosumer.wallet.balance, Currency(50) - kWh(10).to_cost(energy_market.buy_price))
        self.assertEqual(prosumer.energy_balance, kWh(10))

    def test_buy_forced(self):
        battery = Battery(kWh(100), 1.0, kWh(50))
        energy_systems = EnergySystems()
        energy_market = EnergyMarket(Currency(0.5), Currency(1))
        prosumer = Prosumer(battery, energy_systems, Currency(50), energy_market)

        prosumer.buy_energy(kWh(10), energy_market.buy_price_forced, forced=True)

        self.assertEqual(prosumer.wallet.balance, Currency(50) - kWh(10).to_cost(energy_market.buy_price_forced))
        self.assertEqual(prosumer.energy_balance, kWh(10))


class TestProsumerSell(unittest.TestCase):

    def test_sell(self):
        battery = Battery(kWh(100), 1.0, kWh(50))
        energy_systems = EnergySystems()
        energy_market = EnergyMarket(Currency(0.5), Currency(1))
        prosumer = Prosumer(battery, energy_systems, Currency(50), energy_market)

        prosumer.sell_energy(kWh(10), energy_market.sell_price)

        self.assertEqual(prosumer.wallet.balance, Currency(50) + kWh(10).to_cost(energy_market.sell_price))
        self.assertEqual(prosumer.energy_balance, kWh(-10))

    def test_sell_forced(self):
        battery = Battery(kWh(100), 1.0, kWh(50))
        energy_systems = EnergySystems()
        energy_market = EnergyMarket(Currency(0.5), Currency(1))
        prosumer = Prosumer(battery, energy_systems, Currency(50), energy_market)

        prosumer.sell_energy(kWh(10), energy_market.sell_price, forced=True)

        self.assertEqual(prosumer.wallet.balance, Currency(50) + kWh(10).to_cost(energy_market.sell_price_forced))
        self.assertEqual(prosumer.energy_balance, kWh(-10))


class TestProsumerConsume(unittest.TestCase):

    def test_consume_less_than_bought_without_forced_sell(self):
        battery = Battery(kWh(100), 1.0, kWh(50))
        energy_systems = EnergySystems()
        energy_market = EnergyMarket(Currency(0.5), Currency(1))
        prosumer = Prosumer(battery, energy_systems, Currency(50), energy_market)

        time = datetime(2022, 1, 1, hour=12)
        prosumer.scheduled_trading_amounts[12] = kWh(10)
        prosumer.scheduled_price_thresholds[12] = energy_market.buy_price
        prosumer.energy_systems.get_consumption_power = lambda t: kW(5)

        prosumer.consume(time)

        self.assertEqual(prosumer.wallet.balance, Currency(50) - kWh(10).to_cost(energy_market.buy_price))
        self.assertEqual(prosumer.battery, kWh(55))
        self.assertEqual(prosumer.energy_balance, kWh(0))

    def test_consume_less_than_bought_with_forced_sell(self):
        battery = Battery(kWh(100), 1.0, kWh(98))
        energy_systems = EnergySystems()
        energy_market = EnergyMarket(Currency(0.5), Currency(1))
        prosumer = Prosumer(battery, energy_systems, Currency(50), energy_market)

        time = datetime(2022, 1, 1, hour=12)
        prosumer.scheduled_trading_amounts[12] = kWh(10)
        prosumer.scheduled_price_thresholds[12] = energy_market.buy_price
        prosumer.energy_systems.get_consumption_power = lambda t: kW(5)

        prosumer.consume(time)
        expected_balance = Currency(50) \
                        - kWh(10).to_cost(energy_market.buy_price) \
                        + kWh(3).to_cost(energy_market.sell_price_forced)
        self.assertEqual(prosumer.wallet.balance, expected_balance)
        self.assertEqual(prosumer.battery, kWh(100))
        self.assertEqual(prosumer.energy_balance, kWh(0))

    def test_consume_more_than_bought_without_forced_buy(self):
        battery = Battery(kWh(100), 1.0, kWh(50))
        energy_systems = EnergySystems()
        energy_market = EnergyMarket(Currency(0.5), Currency(1))
        prosumer = Prosumer(battery, energy_systems, Currency(50), energy_market)

        time = datetime(2022, 1, 1, hour=12)
        prosumer.scheduled_trading_amounts[12] = kWh(10)
        prosumer.scheduled_price_thresholds[12] = energy_market.buy_price
        prosumer.energy_systems.get_consumption_power = lambda t: kW(15)

        prosumer.consume(time)

        self.assertEqual(prosumer.wallet.balance, Currency(50) - kWh(10).to_cost(energy_market.buy_price))
        self.assertEqual(prosumer.battery, kWh(45))
        self.assertEqual(prosumer.energy_balance, kWh(0))

    def test_consume_more_than_bought_with_forced_buy(self):
        battery = Battery(kWh(100), 1.0, kWh(2))
        energy_systems = EnergySystems()
        energy_market = EnergyMarket(Currency(0.5), Currency(1))
        prosumer = Prosumer(battery, energy_systems, Currency(50), energy_market)

        time = datetime(2022, 1, 1, hour=12)
        prosumer.scheduled_trading_amounts[12] = kWh(10)
        prosumer.scheduled_price_thresholds[12] = energy_market.buy_price
        prosumer.energy_systems.get_consumption_power = lambda t: kW(15)

        prosumer.consume(time)
        expected_balance = Currency(50) - kWh(10).to_cost(energy_market.buy_price) - kWh(3).to_cost(
            energy_market.buy_price_forced)
        self.assertEqual(prosumer.wallet.balance, expected_balance)
        self.assertEqual(prosumer.battery, kWh(0))
        self.assertEqual(prosumer.energy_balance, kWh(0))


class TestProsumerProduce(unittest.TestCase):

    def test_produce_more_than_sold_without_forced_sell(self):
        battery = Battery(kWh(100), 1.0, kWh(50))
        energy_systems = EnergySystems()
        energy_market = EnergyMarket(Currency(0.5), Currency(1))
        prosumer = Prosumer(battery, energy_systems, Currency(50), energy_market)

        time = datetime(2022, 1, 1, hour=12)
        prosumer.scheduled_trading_amounts[12] = kWh(-10)
        prosumer.scheduled_price_thresholds[12] = energy_market.sell_price
        prosumer.energy_systems.get_production_power = lambda t: kW(15)

        prosumer.produce(time)

        self.assertEqual(prosumer.wallet.balance, Currency(50) + kWh(10).to_cost(energy_market.sell_price))
        self.assertEqual(prosumer.battery, kWh(55))
        self.assertEqual(prosumer.energy_balance, kWh(0))

    def test_produce_more_than_sold_with_forced_sell(self):
        battery = Battery(kWh(100), 1.0, kWh(98))
        energy_systems = EnergySystems()
        energy_market = EnergyMarket(Currency(0.5), Currency(1))
        prosumer = Prosumer(battery, energy_systems, Currency(50), energy_market)

        time = datetime(2022, 1, 1, hour=12)
        prosumer.scheduled_trading_amounts[12] = kWh(-10)
        prosumer.scheduled_price_thresholds[12] = energy_market.buy_price
        prosumer.energy_systems.get_consumption_power = lambda t: kW(15)

        prosumer.consume(time)
        expected_balance = Currency(50) \
                        + kWh(10).to_cost(energy_market.sell_price) \
                        + kWh(3).to_cost(energy_market.sell_price_forced)
        self.assertEqual(prosumer.wallet.balance, expected_balance)
        self.assertEqual(prosumer.battery, kWh(100))
        self.assertEqual(prosumer.energy_balance, kWh(0))

    def test_produce_less_than_sold_without_forced_buy(self):
        battery = Battery(kWh(100), 1.0, kWh(50))
        energy_systems = EnergySystems()
        energy_market = EnergyMarket(Currency(0.5), Currency(1))
        prosumer = Prosumer(battery, energy_systems, Currency(50), energy_market)

        time = datetime(2022, 1, 1, hour=12)
        prosumer.scheduled_trading_amounts[12] = kWh(-10)
        prosumer.scheduled_price_thresholds[12] = energy_market.sell_price
        prosumer.energy_systems.get_production_power = lambda t: kW(5)

        prosumer.consume(time)

        self.assertEqual(prosumer.wallet.balance, Currency(50) + kWh(10).to_cost(energy_market.sell_price))
        self.assertEqual(prosumer.battery, kWh(45))
        self.assertEqual(prosumer.energy_balance, kWh(0))

    def test_produce_less_than_sold_with_forced_buy(self):
        battery = Battery(kWh(100), 1.0, kWh(2))
        energy_systems = EnergySystems()
        energy_market = EnergyMarket(Currency(0.5), Currency(1))
        prosumer = Prosumer(battery, energy_systems, Currency(50), energy_market)

        time = datetime(2022, 1, 1, hour=12)
        prosumer.scheduled_trading_amounts[12] = kWh(-10)
        prosumer.scheduled_price_thresholds[12] = energy_market.sell_price
        prosumer.energy_systems.get_consumption_power = lambda t: kW(5)

        prosumer.consume(time)
        expected_balance = Currency(50) - kWh(10).to_cost(energy_market.sell_price) - kWh(3).to_cost(
            energy_market.buy_price_forced)
        self.assertEqual(prosumer.wallet.balance, expected_balance)
        self.assertEqual(prosumer.battery, kWh(0))
        self.assertEqual(prosumer.energy_balance, kWh(0))


if __name__ == '__main__':
    unittest.main()
