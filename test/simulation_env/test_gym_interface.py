import unittest

from random_agent import RandomAgent

from ml4trade.simulation_env import SimulationEnv
from ml4trade.constants import START_TIME
from utils import setup_default_data_strategies


class TestSimulationEnv(unittest.TestCase):
    def test_gym_interface_works(self):
        env = SimulationEnv(setup_default_data_strategies())

        model = RandomAgent(env)
        model.learn(total_timesteps=3)

        obs = env.reset()
        for _ in range(4):
            action, _states = model.predict(obs)
            obs, rewards, dones, info = env.step(action)

    def test_step_passes_action_to_prosumer(self):
        env = SimulationEnv(setup_default_data_strategies())
        env.step(env.action_space.sample())
        self.assertIsNotNone(env.prosumer.scheduled_buy_amounts)
        self.assertIsNotNone(env.prosumer.scheduled_sell_amounts)
        self.assertIsNotNone(env.prosumer.scheduled_buy_thresholds)
        self.assertIsNotNone(env.prosumer.scheduled_sell_thresholds)
        self.assertEqual(env.prosumer.next_day_actions, None)

    def test_step_updates_total_reward(self):
        env = SimulationEnv(setup_default_data_strategies())
        total_reward_before = env.total_reward
        env.step(env.action_space.sample())
        self.assertEqual(env.total_reward, total_reward_before + env._calculate_reward())

    def test_step_updates_history(self):
        env = SimulationEnv(setup_default_data_strategies())
        self.assertEqual(len(env.history['total_reward']), 0)
        action = env.action_space.sample()
        env.step(action)
        self.assertEqual(len(env.history['total_reward']), 1)
        self.assertEqual(env.history['total_reward'][0], env.total_reward)
        self.assertEqual(env.history['wallet_balance'][0], env.prosumer.wallet.balance.value)
        self.assertTrue((env.history['action'][0] == action).all())
        self.assertEqual(env.history['tick'][0], env._clock.cur_tick)
        self.assertEqual(env.history['datetime'][0], env._clock.cur_datetime)

    def test_reset_sets_initial_values(self):
        env = SimulationEnv(setup_default_data_strategies())
        env.step(env.action_space.sample())
        env.step(env.action_space.sample())
        self.assertNotEqual(env.prosumer.wallet.balance, env.prosumer_init_balance)
        self.assertNotEqual(env.prev_prosumer_balance, env.prosumer_init_balance)
        self.assertNotEqual(env.prosumer.battery.current_charge, env.battery_init_charge)
        self.assertNotEqual(env._clock.cur_datetime, env.start_datetime)
        self.assertNotEqual(env._clock.cur_tick, env.start_tick)
        env.reset()
        self.assertEqual(env.prosumer.wallet.balance, env.prosumer_init_balance)
        self.assertEqual(env.prev_prosumer_balance, env.prosumer_init_balance)
        self.assertEqual(env.prosumer.battery.current_charge, env.battery_init_charge)
        self.assertEqual(env._clock.cur_datetime, env.start_datetime)
        self.assertEqual(env._clock.cur_tick, env.start_tick)

        self.assertEqual(env.total_reward, 0)
        self.assertEqual(len(env.history['total_reward']), 0)

    def test_reset_starts_new_simulation(self):
        start_datetime = START_TIME.replace(hour=0)
        env = SimulationEnv(setup_default_data_strategies(), start_datetime=start_datetime)
        env.reset()
        self.assertNotEqual(env._clock.cur_datetime, start_datetime)
        self.assertTrue(env._clock.is_it_scheduling_hour())


if __name__ == '__main__':
    unittest.main()
