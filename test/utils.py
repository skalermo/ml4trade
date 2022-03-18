from datetime import datetime, timedelta
from operator import itemgetter


from src.simulation_env import SimulationEnv


def load_from_setup(setup: dict, *args) -> tuple:
    return itemgetter(*args)(setup)


def time_travel(env: SimulationEnv, delta: timedelta):
    env.cur_datetime += delta


def time_travel_to(env: SimulationEnv, new_datetime: datetime):
    assert new_datetime >= env.cur_datetime
    env.cur_datetime = new_datetime
