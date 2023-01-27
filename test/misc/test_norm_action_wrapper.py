from datetime import timedelta
from typing import Union
from unittest import TestCase

import pandas as pd

import utils
from ml4trade.misc.norm_action_wrapper import CUSTOM_ACTION_SPACE, AvgMonthPriceRetriever

from ml4trade.domain.units import MWh
from ml4trade.domain.constants import START_TIME
from ml4trade.misc import ActionWrapper
from ml4trade.misc.interval_wrapper import IntervalWrapper
from utils import setup_default_simulation_env

class TestActionWrapper(TestCase):
    def setUp(self):
        self.end_datetime = START_TIME + timedelta(days=14)
        self.battery_init_charge = MWh(0.1)
        self.env = setup_default_simulation_env(
            end_datetime=self.end_datetime,
            battery_init_charge=self.battery_init_charge
        )
        self.env_wrapper = IntervalWrapper(env=self.env, interval=timedelta(days=1), split_ratio=0.75)
        prices_df = pd.read_csv(utils.prices_pl_path, header=0)
        self.avg_month_price_retriever = AvgMonthPriceRetriever(prices_df)
        self.action_wrapper = ActionWrapper(env=self.env_wrapper, ref_power_MW=1, avg_month_price_retriever=self.avg_month_price_retriever)

    def test_constructor(self):
        self.assertEqual(self.action_wrapper.env, self.env)
        self.assertEqual(self.action_wrapper.env_wrapper, self.env_wrapper)
        self.assertEqual(self.action_wrapper.env.action_space, CUSTOM_ACTION_SPACE)
        self.assertEqual(self.action_wrapper.ref_power_MW, 1)
        self.assertEqual(self.action_wrapper.clock_view, self.env.new_clock_view())
        self.assertEqual(self.action_wrapper._avg_month_price_retriever, self.avg_month_price_retriever)

    def test_action(self):
        self.assertEqual(1,1)

    def test_reverse_action(self):
        self.assertEqual(1,1)


class TestAvgMonthPriceRetriever(TestCase):
    def test_constructor(self):
        self.fail()

    def test_get_prev_month_avg_price(self):
        self.fail()

    def test__get_prev_month(self):
        self.fail()
