import unittest

from ml4trade.history import History
from utils import setup_default_simulation_env


class TestHistory(unittest.TestCase):
    def setUp(self) -> None:
        self.env = setup_default_simulation_env()
        self.history = self.env.history

    def test_constructor(self):
        self.assertIs(self.history._clock_view._clock, self.env._clock)
        self.assertTrue(self.history._history, [])

    def test_tick_update(self):
        history = History(self.env._clock.view())
        self.assertEqual(len(history), 0)

        history.tick_update(
            self.env._prosumer,
            self.env._market,
            self.env._production_system,
            self.env._consumption_system,
        )

        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['tick'], self.env._clock.cur_tick)
        self.assertEqual(history[0]['datetime'], self.env._clock.cur_datetime)
        self.assertEqual(history[0]['wallet_balance'], self.env._prosumer.wallet.balance.value)
        self.assertEqual(history[0]['rel_battery'], self.env._prosumer.battery.rel_current_charge)
        self.assertEqual(history[0]['unscheduled_buy_amount'], self.env._prosumer.last_unscheduled_buy_transaction or (0, False))
        self.assertEqual(history[0]['unscheduled_sell_amount'], self.env._prosumer.last_unscheduled_sell_transaction or (0, False))
        self.assertEqual(history[0]['price'], self.env._market.ds.last_processed)
        self.assertEqual(history[0]['energy_produced'], self.env._production_system.ds.last_processed or 0)
        self.assertEqual(history[0]['energy_consumed'], self.env._consumption_system.ds.last_processed or 0)

    def test_tick_update_existing_row(self):
        history = History(self.env._clock.view())
        history.tick_update(
            self.env._prosumer,
            self.env._market,
            self.env._production_system,
            self.env._consumption_system,
        )
        self.assertEqual(len(history), 1)
        history[0]['price'] = 42
        self.assertEqual(history[0]['price'], 42)

        history.tick_update(
            self.env._prosumer,
            self.env._market,
            self.env._production_system,
            self.env._consumption_system,
        )

        self.assertEqual(len(history), 1)
        self.assertNotEqual(history[0]['price'], 42)

    def test_step_update(self):
        history = History(self.env._clock.view())
        self.assertEqual(len(history), 0)

        action = self.env.action_space.sample()
        history.step_update(action)

        self.assertEqual(len(history), 24 + 24 - 10)
        next_day_history = history._history[-24:]
        self.assertListEqual([r['scheduled_buy_amount'] for r in next_day_history], action[0:24].tolist())
        self.assertListEqual([r['scheduled_sell_amount'] for r in next_day_history], action[24:48].tolist())
        self.assertListEqual([r['scheduled_buy_threshold'] for r in next_day_history], action[48:72].tolist())
        self.assertListEqual([r['scheduled_sell_threshold'] for r in next_day_history], action[72:96].tolist())

    def test_last_day_summary(self):
        history = History(self.env._clock.view())

        def update():
            row = {
                'price': 100,
                'energy_produced': 10,
                'energy_consumed': 2,
            }
            history._history.append(row)

        for _ in range(72 - 11 - 1):
            update()
            self.env._clock.tick()

        update()
        history.step_update(self.env.action_space.sample())
        self.assertEqual(history._last_day_summary(), (0, 0))
        update()

        self.assertNotEqual(history._last_day_summary(), 0)
        potential_profit = history.last_day_potential_profit()
        self.assertEqual(potential_profit, 100 * (10 - 2) * 24)  # 19200


if __name__ == '__main__':
    unittest.main()
