import unittest
from src.battery import Battery
from src.energy_manipulation.energy_systems import EnergySystems
from src.custom_types import kWh, Currency
from src.market import EnergyMarket
from src.prosumer import Prosumer


class TestProsumerBuy(unittest.TestCase):

    def test_buy(self):
        battery = Battery(kWh(100), 1.0, kWh(50))
        energy_systems = EnergySystems()
        energy_market = EnergyMarket(Currency(0.5), Currency(1))
        prosumer = Prosumer(battery, energy_systems, Currency(50), energy_market)

        prosumer.buy_energy(kWh(10), energy_market.buy_price)

        self.assertEqual(prosumer.wallet.balance, Currency(50) - kWh(10).to_cost(energy_market.buy_price))
        self.assertEqual(prosumer.energy_balance.value, kWh(10))

    def test_buy_forced(self):
        battery = Battery(kWh(100), 1.0, kWh(50))
        energy_systems = EnergySystems()
        energy_market = EnergyMarket(Currency(0.5), Currency(1))
        prosumer = Prosumer(battery, energy_systems, Currency(50), energy_market)

        prosumer.buy_energy(kWh(10), energy_market.buy_price_forced, forced=True)

        self.assertEqual(prosumer.wallet.balance, Currency(50) - kWh(10).to_cost(energy_market.buy_price_forced))
        self.assertEqual(prosumer.energy_balance.value, kWh(10))


class TestProsumerSell(unittest.TestCase):

    def test_sell(self):
        battery = Battery(kWh(100), 1.0, kWh(50))
        energy_systems = EnergySystems()
        energy_market = EnergyMarket(Currency(0.5), Currency(1))
        prosumer = Prosumer(battery, energy_systems, Currency(50), energy_market)

        prosumer.sell_energy(kWh(10), energy_market.sell_price)

        self.assertEqual(prosumer.wallet.balance, Currency(50) + kWh(10).to_cost(energy_market.sell_price))
        self.assertEqual(prosumer.energy_balance.value, kWh(-10))

    def test_sell_forced(self):
        battery = Battery(kWh(100), 1.0, kWh(50))
        energy_systems = EnergySystems()
        energy_market = EnergyMarket(Currency(0.5), Currency(1))
        prosumer = Prosumer(battery, energy_systems, Currency(50), energy_market)

        prosumer.sell_energy(kWh(10), energy_market.sell_price, forced=True)

        self.assertEqual(
            prosumer.wallet.balance,
            Currency(50) + kWh(10).to_cost(energy_market.sell_price_forced),
            )
        self.assertEqual(prosumer.energy_balance.value, kWh(-10))


if __name__ == '__main__':
    unittest.main()
