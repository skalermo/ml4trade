from datetime import time, datetime


import numpy as np
import gym


SCHEDULING_TIME = time(hour=10, minute=30)
ACTION_REPLACEMENT_TIME = time(hour=0)  # midnight
START_TIME = datetime(
    year=2022,
    month=3,
    day=8,
    hour=SCHEDULING_TIME.hour,
)

BUY_AMOUNT_BOUND_HIGH = np.inf
SELL_AMOUNT_BOUND_HIGH = np.inf
BUY_PRICE_THRESHOLD_MAX = np.inf
SELL_PRICE_THRESHOLD_MAX = np.inf

# 24 buy amount 24 sell amount 24 price buy thresholds 24 price sell thresholds
# Defines transactions for each hour for the next 24 hours
# starting from ACTION_REPLACEMENT_TIME.
SIMULATION_ENV_ACTION_SPACE = gym.spaces.Box(
    low=np.array([0] * 96),
    high=np.array(
        [BUY_AMOUNT_BOUND_HIGH] * 24
        + [SELL_AMOUNT_BOUND_HIGH] * 24
        + [BUY_PRICE_THRESHOLD_MAX] * 24
        + [SELL_PRICE_THRESHOLD_MAX] * 24
    ),
)
