import unittest
from datetime import datetime

from ml4trade.domain.battery import Battery
from ml4trade.domain.production import ProductionSystem
from ml4trade.domain.prosumer import Prosumer
from ml4trade.domain.units import Currency, MWh
from utils import (
    load_from_setup,
    setup_default_market,
    setup_default_consumption_system,
    setup_default_clock,
)


def _setup(battery_current_charge: MWh = MWh(0.05)) -> dict:
    battery = Battery(MWh(0.1), 1.0, battery_current_charge)
    clock = setup_default_clock(start_datetime=datetime(2022, 1, 1, hour=12))
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

        prosumer.scheduled_buy_amounts[12] = MWh(0.01)
        prosumer.scheduled_buy_thresholds[12] = energy_market.get_buy_price()
        prosumer.consumption_system.calculate_energy = lambda: MWh(0.005)

        prosumer.consume()

        self.assertEqual(prosumer.wallet.balance, Currency(50) - MWh(0.01).to_cost(energy_market.get_buy_price()))
        self.assertEqual(prosumer.battery.current_charge, MWh(0.055))
        self.assertEqual(prosumer.energy_balance.value, MWh(0))

    def test_consume_less_than_bought_with_forced_sell(self):
        prosumer, energy_market = load_from_setup(_setup(MWh(0.098)), 'prosumer', 'energy_market')

        prosumer.scheduled_buy_amounts[12] = MWh(0.01)
        prosumer.scheduled_buy_thresholds[12] = energy_market.get_buy_price()
        prosumer.consumption_system.calculate_energy = lambda: MWh(0.005)

        prosumer.consume()
        expected_balance = Currency(50) \
                           - MWh(0.01).to_cost(energy_market.get_buy_price()) \
                           + MWh(0.003).to_cost(energy_market.get_sell_price_unscheduled())
        self.assertEqual(prosumer.wallet.balance, expected_balance)
        self.assertEqual(prosumer.battery.current_charge, MWh(0.1))
        self.assertEqual(prosumer.energy_balance.value, MWh(0))

    def test_consume_more_than_bought_without_forced_buy(self):
        prosumer, energy_market = load_from_setup(_setup(), 'prosumer', 'energy_market')

        prosumer.scheduled_buy_amounts[12] = MWh(0.01)
        prosumer.scheduled_buy_thresholds[12] = energy_market.get_buy_price()
        prosumer.consumption_system.calculate_energy = lambda: MWh(0.015)

        prosumer.consume()

        self.assertEqual(prosumer.wallet.balance, Currency(50) - MWh(0.01).to_cost(energy_market.get_buy_price()))
        self.assertAlmostEqual(prosumer.battery.current_charge.value, 0.045, 10)
        self.assertEqual(prosumer.energy_balance.value, MWh(0))

    def test_consume_more_than_bought_with_forced_buy(self):
        prosumer, energy_market = load_from_setup(_setup(MWh(0.002)), 'prosumer', 'energy_market')

        prosumer.scheduled_buy_amounts[12] = MWh(0.01)
        prosumer.scheduled_buy_thresholds[12] = energy_market.get_buy_price()
        prosumer.consumption_system.calculate_energy = lambda: MWh(0.015)

        prosumer.consume()
        expected_balance = Currency(50) - MWh(0.01).to_cost(energy_market.get_buy_price()) - MWh(0.003).to_cost(
            energy_market.get_buy_price_unscheduled())
        self.assertEqual(prosumer.wallet.balance, expected_balance)
        self.assertEqual(prosumer.battery.current_charge, MWh(0))
        self.assertEqual(prosumer.energy_balance.value, MWh(0))


class TestProduce(unittest.TestCase):
    def test_produce_more_than_sold_without_forced_sell(self):
        prosumer, energy_market = load_from_setup(_setup(), 'prosumer', 'energy_market')

        prosumer.scheduled_sell_amounts[12] = MWh(0.01)
        prosumer.scheduled_sell_thresholds[12] = energy_market.get_sell_price()
        prosumer.production_system.calculate_energy = lambda: MWh(0.015)

        prosumer.produce()

        self.assertEqual(prosumer.wallet.balance, Currency(50) + MWh(0.01).to_cost(energy_market.get_sell_price()))
        self.assertEqual(prosumer.battery.current_charge, MWh(0.055))
        self.assertEqual(prosumer.energy_balance.value, MWh(0))

    def test_produce_more_than_sold_with_forced_sell(self):
        prosumer, energy_market = load_from_setup(_setup(MWh(0.098)), 'prosumer', 'energy_market')

        prosumer.scheduled_sell_amounts[12] = MWh(0.01)
        prosumer.scheduled_sell_thresholds[12] = energy_market.get_sell_price()
        prosumer.production_system.calculate_energy = lambda: MWh(0.015)

        prosumer.produce()

        expected_balance = Currency(50) + MWh(0.01).to_cost(energy_market.get_sell_price()) + MWh(0.003).to_cost(
            energy_market.get_sell_price_unscheduled())
        self.assertEqual(prosumer.wallet.balance, expected_balance)
        self.assertEqual(prosumer.battery.current_charge, MWh(0.1))
        self.assertEqual(prosumer.energy_balance.value, MWh(0))

    def test_produce_less_than_sold_without_forced_buy(self):
        prosumer, energy_market = load_from_setup(_setup(), 'prosumer', 'energy_market')

        prosumer.scheduled_sell_amounts[12] = MWh(0.01)
        prosumer.scheduled_sell_thresholds[12] = energy_market.get_sell_price()
        prosumer.production_system.calculate_energy = lambda: MWh(0.005)

        prosumer.produce()

        self.assertEqual(prosumer.wallet.balance, Currency(50) + MWh(0.01).to_cost(energy_market.get_sell_price()))
        self.assertAlmostEqual(prosumer.battery.current_charge.value, 0.045, 10)
        self.assertEqual(prosumer.energy_balance.value, MWh(0))

    def test_produce_less_than_sold_with_forced_buy(self):
        prosumer, energy_market = load_from_setup(_setup(MWh(0.002)), 'prosumer', 'energy_market')

        prosumer.scheduled_sell_amounts[12] = MWh(0.01)
        prosumer.scheduled_sell_thresholds[12] = energy_market.get_sell_price()
        prosumer.production_system.calculate_energy = lambda: MWh(0.005)

        prosumer.produce()

        expected_balance = Currency(50) + MWh(0.01).to_cost(energy_market.get_sell_price()) - MWh(0.003).to_cost(
            energy_market.get_buy_price_unscheduled())
        self.assertEqual(prosumer.wallet.balance, expected_balance)
        self.assertEqual(prosumer.battery.current_charge, MWh(0))
        self.assertEqual(prosumer.energy_balance.value, MWh(0))


if __name__ == '__main__':
    unittest.main()
