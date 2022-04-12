import unittest
from src.battery import Battery
from src.energy_manipulation.energy_systems import EnergySystems
from src.custom_types import kWh, Currency
from src.prosumer import Prosumer

from utils import setup_default_market


class TestProsumerBuy(unittest.TestCase):

    def test_buy(self):
        battery = Battery(kWh(100), 1.0, kWh(50))
        energy_systems = EnergySystems()
        energy_market = setup_default_market()
        prosumer = Prosumer(battery, energy_systems, Currency(50), energy_market)

        prosumer.buy_energy(kWh(10), energy_market.get_buy_price())

        self.assertEqual(prosumer.wallet.balance, Currency(50) - kWh(10).to_cost(energy_market.get_buy_price()))
        self.assertEqual(prosumer.energy_balance.value, kWh(10))

    def test_buy_forced(self):
        battery = Battery(kWh(100), 1.0, kWh(50))
        energy_systems = EnergySystems()
        energy_market = setup_default_market()
        prosumer = Prosumer(battery, energy_systems, Currency(50), energy_market)

        prosumer.buy_energy(kWh(10), energy_market.get_buy_price_unscheduled(), scheduled=False)

        self.assertEqual(prosumer.wallet.balance, Currency(50) - kWh(10).to_cost(energy_market.get_buy_price_unscheduled()))
        self.assertEqual(prosumer.energy_balance.value, kWh(10))


class TestProsumerSell(unittest.TestCase):

    def test_sell(self):
        battery = Battery(kWh(100), 1.0, kWh(50))
        energy_systems = EnergySystems()
        energy_market = setup_default_market()
        prosumer = Prosumer(battery, energy_systems, Currency(50), energy_market)

        prosumer.sell_energy(kWh(10), energy_market.get_sell_price())

        self.assertEqual(prosumer.wallet.balance, Currency(50) + kWh(10).to_cost(energy_market.get_sell_price()))
        self.assertEqual(prosumer.energy_balance.value, kWh(-10))

    def test_sell_forced(self):
        battery = Battery(kWh(100), 1.0, kWh(50))
        energy_systems = EnergySystems()
        energy_market = setup_default_market()
        prosumer = Prosumer(battery, energy_systems, Currency(50), energy_market)

        prosumer.sell_energy(kWh(10), energy_market.get_sell_price(), scheduled=False)

        self.assertEqual(
            prosumer.wallet.balance,
            Currency(50) + kWh(10).to_cost(energy_market.get_sell_price_unscheduled()),
            )
        self.assertEqual(prosumer.energy_balance.value, kWh(-10))


if __name__ == '__main__':
    unittest.main()
