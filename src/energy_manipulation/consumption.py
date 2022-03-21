from typing import Callable
import random
from src.custom_types import kW


def _default_callback(date):
    return kW(5.47*(1+random.gauss(5.47, 0.3)))
    # 5,47 - average daily energy consumption per power consumer
    # (1996 kWh per power consumer per year according to data from
    # https://www.cire.pl/artykuly/serwis-informacyjny-cire-24/gus-zuzycie-energii-elektrycznej-w-gosp-domowych-wzroslo-o-3-rr-w-2020-r


class ConsumptionSystem:
    def get_power(self, date, callback: Callable = _default_callback) -> kW:
        return callback(date)
