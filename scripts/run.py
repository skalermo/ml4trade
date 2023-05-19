import os
from typing import List, Dict, Tuple

from datetime import datetime, time, timedelta

import pandas as pd
from stable_baselines3 import A2C
import hydra
from omegaconf import DictConfig, OmegaConf
import quantstats as qs

from ml4trade.data_strategies import ImgwDataStrategy, HouseholdEnergyConsumptionDataStrategy, PricesPlDataStrategy, imgw_col_ids
from ml4trade.simulation_env import SimulationEnv
from ml4trade.domain.units import *


def get_all_csv_filenames(path: str) -> List[str]:
    return [f for f in os.listdir(path) if f.endswith('.csv')]


def setup_sim_env(cfg: DictConfig) -> (SimulationEnv, SimulationEnv):
    orig_cwd = hydra.utils.get_original_cwd()

    weather_data_path = f'{orig_cwd}/../data/.data/weather_unzipped_flattened'
    filenames = get_all_csv_filenames(weather_data_path)
    dfs = []
    for f in filenames:
        df = pd.read_csv(f'{weather_data_path}/{f}', header=None, encoding='cp1250',
                         names=imgw_col_ids.keys(), usecols=imgw_col_ids.values())
        dfs.append(df)
    weather_df: pd.DataFrame = pd.concat(dfs, axis=0, ignore_index=True)
    del dfs
    # 352200375 - station_code for Warszawa Okecie
    weather_df = weather_df.loc[weather_df['code'] == 352200375]
    weather_df.sort_values(by=['year', 'month', 'day', 'hour'], inplace=True)
    weather_df.fillna(method='bfill', inplace=True)

    prices_pl_path = f'{orig_cwd}/../data/.data/prices_pl.csv'
    prices_df: pd.DataFrame = pd.read_csv(prices_pl_path, header=0)
    prices_df.fillna(method='bfill', inplace=True)

    prices_df['index'] = pd.to_datetime(prices_df['index'])
    avg_month_prices: Dict[Tuple[int, int], float] = prices_df.groupby(
        [prices_df['index'].dt.year.rename('year'), prices_df['index'].dt.month.rename('month')]
    )['Fixing I Price [PLN/MWh]'].mean().to_dict()

    data_strategies = {
        'production': ImgwDataStrategy(weather_df, window_size=24, window_direction='forward',
                                       max_solar_power=MW(cfg.energy_systems.max_solar_power),
                                       solar_efficiency=cfg.energy_systems.solar_efficiency,
                                       max_wind_power=MW(cfg.energy_systems.max_wind_power),
                                       max_wind_speed=cfg.energy_systems.max_wind_speed),
        'consumption': HouseholdEnergyConsumptionDataStrategy(household_number=cfg.energy_systems.households,
                                                              window_size=24),
        'market': PricesPlDataStrategy(prices_df)
    }

    env_train = SimulationEnv(
        data_strategies,
        start_datetime=datetime.fromisoformat(cfg.time.ep_start),
        end_datetime=datetime.fromisoformat(cfg.time.ep_end),
        scheduling_time=time.fromisoformat(cfg.time.scheduling),
        action_replacement_time=time.fromisoformat(cfg.time.action_repl),
        prosumer_init_balance=Currency(cfg.wallet.init_balance),
        battery_capacity=MWh(cfg.battery.capacity),
        battery_init_charge=MWh(cfg.battery.init_charge),
        battery_efficiency=cfg.battery.efficiency,
    )
    env_test = SimulationEnv(
        data_strategies,
        start_datetime=datetime.fromisoformat(cfg.time.ep_end),
        end_datetime=datetime.fromisoformat(cfg.time.ep_end) + timedelta(days=365),
        scheduling_time=time.fromisoformat(cfg.time.scheduling),
        action_replacement_time=time.fromisoformat(cfg.time.action_repl),
        prosumer_init_balance=Currency(cfg.wallet.init_balance),
        battery_capacity=MWh(cfg.battery.capacity),
        battery_init_charge=MWh(cfg.battery.init_charge),
        battery_efficiency=cfg.battery.efficiency,
    )
    return env_train, env_test


@hydra.main(config_path='conf', config_name='config')
def main(cfg: DictConfig) -> None:
    print(OmegaConf.to_yaml(cfg))
    env_train, env_test = setup_sim_env(cfg)
    model = A2C('MlpPolicy', env_train, verbose=1)
    model.learn(total_timesteps=1_000)

    obs, _ = env_test.reset()
    done = False
    while not done:
        action, _states = model.predict(obs)
        obs, rewards, _, done, info = env_test.step(action)

    env_test.render_all()

    qs.extend_pandas()
    net_worth = pd.Series(env_test.history['wallet_balance'], index=env_test.history['datetime'])
    returns = net_worth.pct_change().iloc[1:]
    # qs.reports.full(returns)
    qs.reports.html(returns, output='a2c_quantstats.html', download_filename='a2c_quantstats.html')


if __name__ == '__main__':
    main()
