import unittest

from utils import setup_default_simulation_env


class TestDrySimulation(unittest.TestCase):
    def test_predicts_battery_charge(self):
        env = setup_default_simulation_env()
        env.reset(seed=0)

        action = env.action_space.sample()
        # first 10 hours only sell
        # next 14 hours only buy
        action[24:48] = [100] * 10 + [0] * 14
        action[72:96] = [0] * 10 + [10000] * 14
        action[:24] = [0] * 10 + [100] * 14
        action[48:72] = [0] * 10 + [10000] * 14

        env.step(action)
        predicted_rel_battery_charge = env._dry_simulation(24 - 10)
        self.assertEqual(env._prosumer.battery.rel_current_charge, 0)
        self.assertEqual(predicted_rel_battery_charge, 1)

    def test_preserves_original_state(self):
        env = setup_default_simulation_env()
        env.step(env.action_space.sample())
        env.step(env.action_space.sample())
        state_before = (
            env._prev_prosumer_balance,
            env._prosumer_balance,
            env._prosumer.wallet.balance,
            env._prosumer.battery.current_charge,
            env._clock.cur_datetime,
            env._clock.cur_tick,
        )
        env._dry_simulation(24 - 10)
        state_after = (
            env._prev_prosumer_balance,
            env._prosumer_balance,
            env._prosumer.wallet.balance,
            env._prosumer.battery.current_charge,
            env._clock.cur_datetime,
            env._clock.cur_tick,
        )
        self.assertEqual(state_before, state_after)


if __name__ == '__main__':
    unittest.main()
