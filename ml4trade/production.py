from typing import List

from ml4trade.clock import ClockView
from ml4trade.units import MW
from ml4trade.data_strategies.base import DataStrategy


class ProductionSystem:
    def __init__(self, ds: DataStrategy, clock_view: ClockView = None, max_solar_power: MW = MW(0.001),
                 solar_efficiency: float = 0.2, max_wind_power: MW = MW(0.01), max_wind_speed: float = 11):
        self.ds = ds
        self.clock_view = clock_view
        self.max_solar_power = max_solar_power
        self.solar_efficiency = solar_efficiency
        self.max_wind_power = max_wind_power
        self.max_wind_speed = max_wind_speed

    def calculate_power(self) -> MW:
        cur_tick = self.clock_view.cur_tick()
        return self.ds.process(cur_tick)

    def observation(self) -> List[float]:
        cur_tick = self.clock_view.cur_tick()
        return self.ds.observation(cur_tick)
