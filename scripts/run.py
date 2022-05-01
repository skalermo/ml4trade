import os
import sys

from datetime import datetime, time

import pandas as pd
from stable_baselines3 import A2C
import hydra
from omegaconf import DictConfig, OmegaConf

# normally you wouldn't need this
# you would just pip-install the project and import it
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_strategies import ImgwWindDataStrategy, HouseholdEnergyConsumptionDataStrategy, PricesPlDataStrategy, \
    imgw_col_ids
from src.simulation_env import SimulationEnv
from src.units import *


def setup_sim_env(cfg: DictConfig) -> SimulationEnv:
    orig_cwd = hydra.utils.get_original_cwd()
    weather_data_path = f'{orig_cwd}/../data/.data/weather_unzipped_flattened/s_t_02_2022.csv'
    weather_df = pd.read_csv(weather_data_path, header=None, names=imgw_col_ids.keys(), usecols=imgw_col_ids.values(),
                             encoding='cp1250')
    prices_pl_path = f'{orig_cwd}/../data/.data/prices_pl.csv'

    prices_df = pd.read_csv(prices_pl_path, header=0)

    data_strategies = {
        'production': ImgwWindDataStrategy(weather_df, window_size=24, window_direction='forward'),
        'consumption': HouseholdEnergyConsumptionDataStrategy(window_size=24),
        'market': PricesPlDataStrategy(prices_df, window_size=24, window_direction='backward')
    }

    env = SimulationEnv(
        data_strategies,
        start_datetime=datetime.fromisoformat(cfg.time.ep_start),
        end_datetime=datetime.fromisoformat(cfg.time.ep_end),
        scheduling_time=time.fromisoformat(cfg.time.scheduling),
        action_replacement_time=time.fromisoformat(cfg.time.action_repl),
        prosumer_init_balance=Currency(cfg.wallet.init_balance),
        battery_capacity=kWh(cfg.battery.capacity),
        battery_init_charge=kWh(cfg.battery.init_charge),
        battery_efficiency=cfg.battery.efficiency,
    )
    return env


@hydra.main(config_path='conf', config_name='config')
def main(cfg: DictConfig) -> None:
    print(OmegaConf.to_yaml(cfg))
    env = setup_sim_env(cfg)
    model = A2C('MlpPolicy', env, verbose=1)
    model.learn(total_timesteps=1_000)

    obs = env.reset()
    for i in range(100):
        action, _states = model.predict(obs)
        obs, rewards, done, info = env.step(action)
        if done:
            break


if __name__ == '__main__':
    main()
