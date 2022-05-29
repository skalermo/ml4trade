import unittest

import numpy as np

from ml4trade.domain.units import MWh, Currency
from ml4trade.domain.prosumer import Prosumer
from ml4trade.domain.battery import Battery
from ml4trade.domain.production import ProductionSystem
from ml4trade.domain.constants import SIMULATION_ENV_ACTION_SPACE
from ml4trade.domain.clock import SimulationClock
from utils import setup_default_consumption_system


class TestSetNewActions(unittest.TestCase):
    def setUp(self) -> None:
        clock = SimulationClock()
        self.prosumer = Prosumer(
            battery=Battery(),
            clock_view=clock.view(),
            production_system=ProductionSystem(None, None),
            consumption_system=setup_default_consumption_system(clock)
        )
        self.action = SIMULATION_ENV_ACTION_SPACE.sample()
        self.prosumer.schedule(self.action)

    def test_set_new_buy_amounts(self):
        self.assertIsNone(self.prosumer.scheduled_buy_amounts)

        self.prosumer.set_new_actions()

        self.assertTrue(np.array_equal(
            self.prosumer.scheduled_buy_amounts,
            [MWh(a) for a in self.action[0:24]]
        ))

    def test_set_new_sell_amounts(self):
        self.assertIsNone(self.prosumer.scheduled_sell_amounts)

        self.prosumer.set_new_actions()

        self.assertTrue(np.array_equal(
            self.prosumer.scheduled_sell_amounts,
            [MWh(a) for a in self.action[24:48]]
        ))

    def test_set_new_buy_thresholds(self):
        self.assertIsNone(self.prosumer.scheduled_buy_thresholds)

        self.prosumer.set_new_actions()

        self.assertTrue(np.array_equal(
            self.prosumer.scheduled_buy_thresholds,
            [Currency(a) for a in self.action[48:72]]
        ))

    def test_set_new_sell_thresholds(self):
        self.assertIsNone(self.prosumer.scheduled_sell_thresholds)

        self.prosumer.set_new_actions()

        self.assertTrue(np.array_equal(
            self.prosumer.scheduled_sell_thresholds,
            [Currency(a) for a in self.action[72:96]]
        ))

    def test_next_day_actions(self):
        self.assertIsNotNone(self.prosumer.next_day_actions)

        self.prosumer.set_new_actions()

        self.assertIsNone(self.prosumer.next_day_actions)
