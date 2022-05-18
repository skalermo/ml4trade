import unittest

from random_agent import RandomAgent

from ml4trade.simulation_env import SimulationEnv
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

    def test_reset(self):
        env = SimulationEnv(setup_default_data_strategies())
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


if __name__ == '__main__':
    unittest.main()
