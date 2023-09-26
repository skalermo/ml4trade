from ml4trade.data_strategies import DataStrategy
from ml4trade.domain.clock import ClockView

from ml4trade.domain.units import MWh


class PotentialCalculator:
    def __init__(self, clock_view: ClockView, production_ds: DataStrategy, consumption_ds: DataStrategy, prices_ds: DataStrategy,
                 battery_cap: MWh = MWh(2), battery_efficiency: float = 0.85):
        self._battery_efficiency = battery_efficiency
        self._battery_cap = battery_cap
        self._clock_view = clock_view
        self._tick_offset = clock_view.cur_tick()
        self._production_ds = production_ds
        self._consumption_ds = consumption_ds
        self._prices_ds = prices_ds

    def cur_day_summary(self):
        start_idx = self._clock_view.cur_tick() - self._clock_view.scheduling_hour()
        end_idx = start_idx + 24

        produced = []
        consumed = []
        prices = []

        for idx in range(start_idx, end_idx):
            produced.append(self._production_ds.process(idx))
            consumed.append(self._consumption_ds.process(idx))
            prices.append(self._prices_ds.process(idx))

        avg_price = sum(prices) / 24

        extra_produced = sum(p - c for p, c in zip(produced, consumed))
        potential_profit = extra_produced * avg_price

        night_low = min(prices[:9])
        day_high = max(prices[9:])
        price_diff_profit = max(0.0, (day_high * self._battery_efficiency - night_low) * self._battery_cap.value)

        # night_low = min(r['price'] for r in last_day_history[:9])
        # day_high = max(r['price'] for r in last_day_history[9:])
        # price_diff_profit = max(0, (day_high * self._battery_efficiency - night_low) * self._battery_cap.value)

        return potential_profit, price_diff_profit

    def cur_day_potential_profit(self):
        potential_profit, _ = self.cur_day_summary()
        return potential_profit

    def cur_day_price_diff_profit(self):
        _, price_diff_profit = self.cur_day_summary()
        return price_diff_profit
