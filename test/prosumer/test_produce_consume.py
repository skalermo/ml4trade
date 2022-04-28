import unittest
from datetime import datetime

from src.prosumer import Prosumer
from src.battery import Battery
from src.production import ProductionSystem
from src.consumption import ConsumptionSystem
from src.custom_types import Currency, kWh, kW
from src.clock import SimulationClock

from utils import load_from_setup, setup_default_market, setup_default_consumption_system


def _setup(battery_current_charge: kWh = kWh(50)) -> dict:
    battery = Battery(kWh(100), 1.0, battery_current_charge)
    clock = SimulationClock(start_datetime=datetime(2022, 1, 1, hour=12))
    production_system = ProductionSystem(None, clock.view())
    consumption_system = setup_default_consumption_system(clock)
    energy_market = setup_default_market(clock=clock)
    prosumer = Prosumer(battery, production_system, consumption_system, clock.view(), Currency(50), energy_market)

    prosumer.scheduled_buy_amounts = [0.0] * 24
    prosumer.scheduled_buy_thresholds = [0.0] * 24
    prosumer.scheduled_sell_amounts = [0.0] * 24
    prosumer.scheduled_sell_thresholds = [0.0] * 24

    return {
        'battery': battery,
        'energy_market': energy_market,
        'prosumer': prosumer,
    }


class TestConsume(unittest.TestCase):
    def test_consume_less_than_bought_without_forced_sell(self):
        prosumer, energy_market = load_from_setup(_setup(), 'prosumer', 'energy_market')
        
        prosumer.scheduled_buy_amounts[12] = kWh(10)
        prosumer.scheduled_buy_thresholds[12] = energy_market.get_buy_price()
        prosumer.consumption_system.calculate_power = lambda: kW(5)

        prosumer.consume()

        self.assertEqual(prosumer.wallet.balance, Currency(50) - kWh(10).to_cost(energy_market.get_buy_price()))
        self.assertEqual(prosumer.battery.current_charge, kWh(55))
        self.assertEqual(prosumer.energy_balance.value, kWh(0))

    def test_consume_less_than_bought_with_forced_sell(self):
        prosumer, energy_market = load_from_setup(_setup(kWh(98)), 'prosumer', 'energy_market')

        prosumer.scheduled_buy_amounts[12] = kWh(10)
        prosumer.scheduled_buy_thresholds[12] = energy_market.get_buy_price()
        prosumer.consumption_system.calculate_power = lambda: kW(5)

        prosumer.consume()
        expected_balance = Currency(50) \
                           - kWh(10).to_cost(energy_market.get_buy_price()) \
                           + kWh(3).to_cost(energy_market.get_sell_price_unscheduled())
        self.assertEqual(prosumer.wallet.balance, expected_balance)
        self.assertEqual(prosumer.battery.current_charge, kWh(100))
        self.assertEqual(prosumer.energy_balance.value, kWh(0))

    def test_consume_more_than_bought_without_forced_buy(self):
        prosumer, energy_market = load_from_setup(_setup(), 'prosumer', 'energy_market')

        prosumer.scheduled_buy_amounts[12] = kWh(10)
        prosumer.scheduled_buy_thresholds[12] = energy_market.get_buy_price()
        prosumer.consumption_system.calculate_power = lambda: kW(15)

        prosumer.consume()

        self.assertEqual(prosumer.wallet.balance, Currency(50) - kWh(10).to_cost(energy_market.get_buy_price()))
        self.assertEqual(prosumer.battery.current_charge, kWh(45))
        self.assertEqual(prosumer.energy_balance.value, kWh(0))

    def test_consume_more_than_bought_with_forced_buy(self):
        prosumer, energy_market = load_from_setup(_setup(kWh(2)), 'prosumer', 'energy_market')

        prosumer.scheduled_buy_amounts[12] = kWh(10)
        prosumer.scheduled_buy_thresholds[12] = energy_market.get_buy_price()
        prosumer.consumption_system.calculate_power = lambda: kW(15)

        prosumer.consume()
        expected_balance = Currency(50) - kWh(10).to_cost(energy_market.get_buy_price()) - kWh(3).to_cost(
            energy_market.get_buy_price_unscheduled())
        self.assertEqual(prosumer.wallet.balance, expected_balance)
        self.assertEqual(prosumer.battery.current_charge, kWh(0))
        self.assertEqual(prosumer.energy_balance.value, kWh(0))


class TestProduce(unittest.TestCase):
    def test_produce_more_than_sold_without_forced_sell(self):
        prosumer, energy_market = load_from_setup(_setup(), 'prosumer', 'energy_market')

        prosumer.scheduled_sell_amounts[12] = kWh(10)
        prosumer.scheduled_sell_thresholds[12] = energy_market.get_sell_price()
        prosumer.production_system.calculate_power = lambda: kW(15)

        prosumer.produce()

        self.assertEqual(prosumer.wallet.balance, Currency(50) + kWh(10).to_cost(energy_market.get_sell_price()))
        self.assertEqual(prosumer.battery.current_charge, kWh(55))
        self.assertEqual(prosumer.energy_balance.value, kWh(0))

    def test_produce_more_than_sold_with_forced_sell(self):
        prosumer, energy_market = load_from_setup(_setup(kWh(98)), 'prosumer', 'energy_market')

        prosumer.scheduled_sell_amounts[12] = kWh(10)
        prosumer.scheduled_sell_thresholds[12] = energy_market.get_sell_price()
        prosumer.production_system.calculate_power = lambda: kW(15)

        prosumer.produce()

        expected_balance = Currency(50) + kWh(10).to_cost(energy_market.get_sell_price()) + kWh(3).to_cost(energy_market.get_sell_price_unscheduled())
        self.assertEqual(prosumer.wallet.balance, expected_balance)
        self.assertEqual(prosumer.battery.current_charge, kWh(100))
        self.assertEqual(prosumer.energy_balance.value, kWh(0))

    def test_produce_less_than_sold_without_forced_buy(self):
        prosumer, energy_market = load_from_setup(_setup(), 'prosumer', 'energy_market')

        prosumer.scheduled_sell_amounts[12] = kWh(10)
        prosumer.scheduled_sell_thresholds[12] = energy_market.get_sell_price()
        prosumer.production_system.calculate_power = lambda: kW(5)

        prosumer.produce()

        self.assertEqual(prosumer.wallet.balance, Currency(50) + kWh(10).to_cost(energy_market.get_sell_price()))
        self.assertEqual(prosumer.battery.current_charge, kWh(45))
        self.assertEqual(prosumer.energy_balance.value, kWh(0))

    def test_produce_less_than_sold_with_forced_buy(self):
        prosumer, energy_market = load_from_setup(_setup(kWh(2)), 'prosumer', 'energy_market')

        prosumer.scheduled_sell_amounts[12] = kWh(10)
        prosumer.scheduled_sell_thresholds[12] = energy_market.get_sell_price()
        prosumer.production_system.calculate_power = lambda: kW(5)

        prosumer.produce()

        expected_balance = Currency(50) + kWh(10).to_cost(energy_market.get_sell_price()) - kWh(3).to_cost(energy_market.get_buy_price_unscheduled())
        self.assertEqual(prosumer.wallet.balance, expected_balance)
        self.assertEqual(prosumer.battery.current_charge, kWh(0))
        self.assertEqual(prosumer.energy_balance.value, kWh(0))


if __name__ == '__main__':
    unittest.main()
