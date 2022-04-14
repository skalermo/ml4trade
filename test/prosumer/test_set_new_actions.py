import unittest

import numpy as np

from src.custom_types import kWh, Currency
from src.prosumer import Prosumer
from src.battery import Battery
from src.energy_manipulation.energy_systems import EnergySystems
from src.constants import SIMULATION_ENV_ACTION_SPACE


class TestSetNewActions(unittest.TestCase):
    def setUp(self) -> None:
        self.prosumer = Prosumer(
            battery=Battery(),
            energy_systems=EnergySystems(),
        )
        self.action = SIMULATION_ENV_ACTION_SPACE.sample()
        self.prosumer.schedule(self.action)

    def test_set_new_buy_amounts(self):
        self.assertIsNone(self.prosumer.scheduled_buy_amounts)

        self.prosumer.set_new_actions()

        self.assertTrue(np.array_equal(
            self.prosumer.scheduled_buy_amounts,
            [kWh(a) for a in self.action[0:24]]
        ))

    def test_set_new_sell_amounts(self):
        self.assertIsNone(self.prosumer.scheduled_sell_amounts)

        self.prosumer.set_new_actions()

        self.assertTrue(np.array_equal(
            self.prosumer.scheduled_sell_amounts,
            [kWh(a) for a in self.action[24:48]]
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
