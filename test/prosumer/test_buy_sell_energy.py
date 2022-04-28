import unittest
from src.battery import Battery
from src.clock import SimulationClock
from src.production import ProductionSystem
from src.custom_types import kWh, Currency
from src.prosumer import Prosumer

from utils import setup_default_market, setup_default_consumption_system


class TestProsumerBuySell(unittest.TestCase):
    def setUp(self):
        battery = Battery()
        production_system = ProductionSystem(None, None)
        consumption_system = setup_default_consumption_system()
        self.energy_market = setup_default_market()
        self.prosumer = Prosumer(battery, production_system, consumption_system, SimulationClock().view(), Currency(50), self.energy_market)

    def test_buy(self):
        self.prosumer.buy_energy(kWh(10), self.energy_market.get_buy_price())

        self.assertEqual(self.prosumer.wallet.balance, Currency(50) - kWh(10).to_cost(self.energy_market.get_buy_price()))
        self.assertEqual(self.prosumer.energy_balance.value, kWh(10))

    def test_buy_unscheduled(self):
        self.prosumer.buy_energy(kWh(10), self.energy_market.get_buy_price_unscheduled(), scheduled=False)

        self.assertEqual(self.prosumer.wallet.balance, Currency(50) - kWh(10).to_cost(self.energy_market.get_buy_price_unscheduled()))
        self.assertEqual(self.prosumer.energy_balance.value, kWh(10))

    def test_sell(self):
        self.prosumer.sell_energy(kWh(10), self.energy_market.get_sell_price())

        self.assertEqual(self.prosumer.wallet.balance, Currency(50) + kWh(10).to_cost(self.energy_market.get_sell_price()))
        self.assertEqual(self.prosumer.energy_balance.value, kWh(-10))

    def test_sell_unscheduled(self):
        self.prosumer.sell_energy(kWh(10), self.energy_market.get_sell_price(), scheduled=False)

        self.assertEqual(
            self.prosumer.wallet.balance,
            Currency(50) + kWh(10).to_cost(self.energy_market.get_sell_price_unscheduled()),
        )
        self.assertEqual(self.prosumer.energy_balance.value, kWh(-10))


if __name__ == '__main__':
    unittest.main()
