from datetime import timedelta, datetime, time
from typing import List

from ml4trade.data_strategies import DataStrategy


def timedelta_to_hours(td: timedelta) -> int:
    return td.days * 24 + td.seconds // 3600


def calc_tick_offset(data_strategies: List[DataStrategy], scheduling_time: time) -> int:
    start_idx = max([s.observation_size() for s in data_strategies if s.window_direction == 'backward'], default=0)
    return start_idx + scheduling_time.hour


def dfs_are_long_enough(data_strategies: List[DataStrategy], start_datetime: datetime, end_datetime: datetime,
                        start_tick: int) -> bool:
    dfs_lengths = [len(ds.df) for ds in data_strategies if ds.df is not None]
    episode_hour_length = timedelta_to_hours(end_datetime - start_datetime)
    return episode_hour_length + start_tick <= min(dfs_lengths)
