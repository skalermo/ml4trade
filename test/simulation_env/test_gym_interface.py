import unittest
from datetime import timedelta

from ml4trade.domain.constants import START_TIME
from ml4trade.domain.units import MWh
from random_agent import RandomAgent
from utils import setup_default_simulation_env


class TestSimulationEnv(unittest.TestCase):
    def test_gym_interface_works(self):
        env = setup_default_simulation_env()

        model = RandomAgent(env)
        model.learn(total_timesteps=3)

        obs = env.reset()
        for _ in range(4):
            action, _states = model.predict(obs)
            obs, reward, terminated, truncated, info = env.step(action)

    def test_step_passes_action_to_prosumer(self):
        env = setup_default_simulation_env()
        env.step(env.action_space.sample())
        self.assertIsNotNone(env._prosumer.scheduled_buy_amounts)
        self.assertIsNotNone(env._prosumer.scheduled_sell_amounts)
        self.assertIsNotNone(env._prosumer.scheduled_buy_thresholds)
        self.assertIsNotNone(env._prosumer.scheduled_sell_thresholds)
        self.assertEqual(env._prosumer.next_day_actions, None)

    def test_step_updates_history(self):
        env = setup_default_simulation_env()
        len_before = len(env.history)
        env.step(env.action_space.sample())
        self.assertGreater(len(env.history), len_before)
        last_tick_idx = env._clock.cur_tick - env._start_tick - 1
        self.assertEqual(env.history[last_tick_idx]['wallet_balance'], env._prosumer.wallet.balance.value)
        self.assertEqual(env.history[last_tick_idx]['tick'], env._clock.cur_tick - 1)
        self.assertEqual(env.history[last_tick_idx]['datetime'], env._clock.cur_datetime - timedelta(hours=1))

    def test_reset_sets_initial_values(self):
        env = setup_default_simulation_env(battery_init_charge=MWh(0.001))
        env.step(env.action_space.sample())
        env.step(env.action_space.sample())
        env.step(env.action_space.sample())
        self.assertNotEqual(env._prosumer.wallet.balance, env._prosumer_init_balance)
        self.assertNotEqual(env._prev_prosumer_balance, env._prosumer_init_balance)
        self.assertNotEqual(env._prosumer_balance, env._prosumer_init_balance)
        self.assertNotEqual(env._prosumer.battery.current_charge, env._battery_init_charge)
        self.assertNotEqual(env._clock.cur_datetime, env._start_datetime)
        self.assertNotEqual(env._clock.cur_tick, env._start_tick)

        # force reset() to immediately yield
        env._clock.scheduling_time = env._start_datetime
        env.reset()

        self.assertEqual(env._prosumer.wallet.balance, env._prosumer_init_balance)
        self.assertEqual(env._prev_prosumer_balance, env._prosumer_init_balance)
        self.assertEqual(env._prosumer_balance, env._prosumer_init_balance)
        self.assertEqual(env._prosumer.battery.current_charge, env._battery_init_charge)
        self.assertEqual(env._clock.cur_datetime, env._start_datetime)
        self.assertEqual(env._clock.cur_tick, env._start_tick)

    def test_reset_starts_new_simulation(self):
        start_datetime = START_TIME.replace(hour=0)
        env = setup_default_simulation_env(start_datetime=start_datetime)
        env.reset()
        self.assertNotEqual(env._clock.cur_datetime, start_datetime)
        self.assertTrue(env._clock.is_it_scheduling_hour())
        self.assertEqual(len(env.history), 0)

    def test_reset_seeds_environment(self):
        seed = 42
        env = setup_default_simulation_env()
        env2 = setup_default_simulation_env()
        env.reset(seed=seed)
        env2.reset(seed=seed)
        for i in range(10):
            action = env.action_space.sample()
            env.step(action)
            env2.step(action)
        for i, (row, row2) in enumerate(zip(env.history._history, env2.history._history)):
            self.assertDictEqual(row, row2)


if __name__ == '__main__':
    unittest.main()
