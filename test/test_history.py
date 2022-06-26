import unittest

from ml4trade.history import History, tick_history_keys, step_history_keys
from ml4trade.simulation_env import SimulationEnv
from ml4trade.domain.market import UNSCHEDULED_MULTIPLIER
from utils import setup_default_data_strategies


class TestHistory(unittest.TestCase):
    def setUp(self) -> None:
        self.env = SimulationEnv(data_strategies=setup_default_data_strategies())
        self.history = self.env.history

    def test_constructor(self):
        self.assertIs(self.history._clock_view._clock, self.env._clock)
        self.assertTrue(all(k in self.history._history for k in tick_history_keys + step_history_keys))

    def test_tick_update(self):
        history = History(self.env._clock.view())
        self.assertEqual(len(history['tick']), 0)

        history.tick_update(
            self.env._prosumer,
            self.env._market,
            self.env._production_system,
            self.env._consumption_system,
        )

        self.assertEqual(len(history['tick']), 1)
        self.assertEqual(history['tick'][0], self.env._clock.cur_tick)
        self.assertEqual(history['datetime'][0], self.env._clock.cur_datetime)
        self.assertEqual(history['wallet_balance'][0], self.env._prosumer.wallet.balance.value)
        self.assertEqual(history['scheduled_buy_amounts'][0], self.env._prosumer.last_scheduled_buy_transaction)
        self.assertEqual(history['scheduled_sell_amounts'][0], self.env._prosumer.last_scheduled_sell_transaction)
        self.assertEqual(history['battery'][0], self.env._prosumer.battery.rel_current_charge)
        self.assertEqual(history['unscheduled_buy_amounts'][0], self.env._prosumer.last_unscheduled_buy_transaction or (0, False))
        self.assertEqual(history['unscheduled_sell_amounts'][0], self.env._prosumer.last_unscheduled_sell_transaction or (0, False))
        self.assertEqual(history['price'][0], self.env._market.ds.last_processed)
        self.assertEqual(history['energy_produced'][0], self.env._production_system.ds.last_processed)
        self.assertEqual(history['energy_consumed'][0], self.env._consumption_system.ds.last_processed)

    def test_step_update(self):
        self.assertEqual(len(self.history['step_tick']), 0)

        action = self.env.action_space.sample()
        self.history.step_update(action, balance_diff=1)

        self.assertEqual(len(self.history['step_tick']), 1)
        self.assertEqual(self.history['step_tick'][0], self.env._clock.cur_tick)
        self.assertEqual(self.history['step_datetime'][0], self.env._clock.cur_datetime)
        self.assertEqual(self.history['action'][0], action.tolist())
        self.assertEqual(self.history['balance_diff'][0], 1)
        self.assertEqual(self.history['potential_profit'][0], 0)
        self.assertEqual(self.history['unscheduled_sell_actions_profit'][0], 0)
        self.assertEqual(self.history['unscheduled_buy_actions_loss'][0], 0)

    def test_save_reward(self):
        self.assertEqual(len(self.history['reward']), 0)
        self.history.save_reward(1)
        self.assertEqual(len(self.history['reward']), 1)
        self.assertEqual(self.history['reward'][0], 1)

    def test_remove_last_tick_entries(self):
        history = History(self.env._clock.view())
        for _ in range(10):
            history.tick_update(
                self.env._prosumer,
                self.env._market,
                self.env._production_system,
                self.env._consumption_system,
            )
            history.step_update(self.env.action_space.sample(), balance_diff=1)
        self.assertEqual(len(history['tick']), 10)
        history.remove_last_tick_entries(3)
        self.assertEqual(len(history['tick']), 7)
        self.assertEqual(len(history['step_tick']), 10)

    def test_last_day_summary(self):
        history = History(self.env._clock.view())

        def update():
            history._history['tick'].append(0)
            history._history['price'].append(100)
            history._history['energy_produced'].append(10)
            history._history['energy_consumed'].append(2)
            history._history['unscheduled_buy_amounts'].append((4, True))
            history._history['unscheduled_sell_amounts'].append((6, True))

        for _ in range(72 - 11):
            update()

        self.assertEqual(history._last_day_summary(), (0, 0, 0))
        update()
        self.assertNotEqual(history._last_day_summary(), (0, 0, 0))

        for _ in range(10):
            history._history['price'].append(200)

        (
            potential_profit,
            unscheduled_sell_actions_profit,
            unscheduled_buy_actions_loss,
        ) = history._last_day_summary()
        self.assertEqual(potential_profit, 800 * 24)
        self.assertEqual(unscheduled_sell_actions_profit, 600 * 24 / UNSCHEDULED_MULTIPLIER)
        self.assertEqual(unscheduled_buy_actions_loss, 400 * 24 * UNSCHEDULED_MULTIPLIER)

        self.env._clock.tick()
        history._history['price'].append(200)

        (
            potential_profit,
            unscheduled_sell_actions_profit,
            unscheduled_buy_actions_loss,
        ) = history._last_day_summary()
        self.assertEqual(potential_profit, 800 * 24)
        self.assertEqual(unscheduled_sell_actions_profit, 600 * 24 / UNSCHEDULED_MULTIPLIER)
        self.assertEqual(unscheduled_buy_actions_loss, 400 * 24 * UNSCHEDULED_MULTIPLIER)


if __name__ == '__main__':
    unittest.main()
