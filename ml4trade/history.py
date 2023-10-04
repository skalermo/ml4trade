import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict

import numpy as np

from ml4trade.domain.units import MWh
from ml4trade.domain.clock import ClockView
from ml4trade.domain.consumption import ConsumptionSystem
from ml4trade.domain.market import EnergyMarket
from ml4trade.domain.production import ProductionSystem
from ml4trade.domain.prosumer import Prosumer
from ml4trade.rendering.charts import render_all


class History:
    columns = [
        'tick', 'datetime'
        'energy_produced', 'energy_consumed', 'rel_battery',
        'price', 'wallet_balance',
        'scheduled_buy_amount', 'scheduled_sell_amount',
        'scheduled_buy_threshold', 'scheduled_sell_threshold',
        'unscheduled_buy_amount', 'unscheduled_sell_amount',
        'potential_profit',
    ]

    def __init__(self, clock_view: Optional[ClockView] = None, battery_cap: MWh = MWh(2), battery_efficiency: float = 0.85):
        if clock_view is not None:
            self._clock_view = clock_view
            self._tick_offset = clock_view.cur_tick()
        self._history: List[Dict] = []
        self._battery_cap = battery_cap
        self._battery_efficiency = battery_efficiency

    def __getitem__(self, item):
        return self._history[item]

    def __len__(self):
        return len(self._history)

    def _cur_tick_to_idx(self) -> int:
        return self._clock_view.cur_tick() - self._tick_offset

    def tick_update(
            self,
            prosumer: Prosumer,
            market: EnergyMarket,
            production_system: ProductionSystem,
            consumption_system: ConsumptionSystem,
    ):
        new_data = {
            'tick': self._clock_view.cur_tick(),
            'datetime': self._clock_view.cur_datetime(),
            'price': market.get_buy_price().value,
            'wallet_balance': prosumer.wallet.balance.value,
            'rel_battery': prosumer.battery.rel_current_charge,
            'energy_produced': production_system.ds.last_processed or 0,
            'energy_consumed': consumption_system.ds.last_processed or 0,
            'unscheduled_buy_amount': prosumer.last_unscheduled_buy_transaction or (0, False),
            'unscheduled_sell_amount': prosumer.last_unscheduled_sell_transaction or (0, False),
        }
        cur_idx = self._cur_tick_to_idx()
        if cur_idx >= len(self._history):
            self._history.append(new_data)
        else:
            self._history[cur_idx].update(new_data)
        prosumer.last_unscheduled_buy_transaction = None
        prosumer.last_unscheduled_sell_transaction = None

    def _add_empty_rows(self, n: int):
        self._history.extend([{} for _ in range(n)])

    def _has_1day_of_history(self) -> bool:
        # max span of time history goes unfilled is
        # 24 - scheduling_hour hours and another 24 hours
        # we need another 24 hours to fill up history
        # with real values
        # rows of next 24 hours are prefilled with scheduled actions
        # 10 -> 10 -> 24 -> 24 | -> 24
        return len(self._history) >= 96 - self._clock_view.scheduling_hour()

    def step_update(self, action: np.ndarray):
        cur_idx = self._cur_tick_to_idx()
        next_day_start = self._clock_view.cur_datetime().replace(hour=0) + timedelta(days=1)
        if cur_idx >= len(self._history):
            self._add_empty_rows(24 - self._clock_view.scheduling_hour())
        actions = [{
            'datetime': next_day_start + timedelta(hours=h),
            'scheduled_buy_amount': action[h].item(),
            'scheduled_sell_amount': action[24 + h].item(),
            'scheduled_buy_threshold': action[48 + h].item(),
            'scheduled_sell_threshold': action[72 + h].item(),
        } for h in range(24)]

        self._history.extend(actions)

        if self._has_1day_of_history():
            potential_profit, price_diff_profit = self._last_day_summary()
            self._history[cur_idx - self._clock_view.cur_datetime().hour - 1].update({
                'potential_profit': potential_profit,
                'price_diff_profit': price_diff_profit,
            })

    def last_day_potential_profit(self) -> float:
        idx = self._cur_tick_to_idx() - self._clock_view.cur_datetime().hour - 1
        history_entry = None if idx < 0 else self._history[idx].get('potential_profit')
        return history_entry or self._last_day_summary()[0]

    def last_day_price_diff_profit(self) -> float:
        idx = self._cur_tick_to_idx() - self._clock_view.cur_datetime().hour - 1
        history_entry = None if idx < 0 else self._history[idx].get('price_diff_profit')
        return history_entry or self._last_day_summary()[1]

    def _last_day_summary(self) -> (float, float):
        if not self._has_1day_of_history():
            return 0, 0

        end_idx = self._cur_tick_to_idx() - self._clock_view.cur_datetime().hour
        start_idx = end_idx - 24 or None
        last_day_history = self._history[start_idx:end_idx]

        avg_price = sum(r['price'] for r in last_day_history) / 24
        extra_produced = sum(r['energy_produced'] - r['energy_consumed'] for r in last_day_history)
        potential_profit = extra_produced * avg_price

        night_low = min(r['price'] for r in last_day_history[:9])
        day_high = max(r['price'] for r in last_day_history[9:])
        price_diff_profit = max(0, (day_high * self._battery_efficiency - night_low) * self._battery_cap.value)

        return potential_profit, price_diff_profit

    def render(self, last_n_days: int = 2, n_days_offset: int = 0, save_path=None):
        render_all(self._history, last_n_days, n_days_offset, save_path)

    def save(self, path: str = 'env_history.json'):
        with open(path, 'w') as f:
            json.dump(self._history, f, indent=2, default=str)

    @classmethod
    def load(cls, path: str, clock_view: Optional[ClockView] = None) -> 'History':
        with open(path, 'r') as f:
            history = json.load(f)

        for r in history:
            r['datetime'] = datetime.fromisoformat(r['datetime'])

            # fixes past results generated by bugged code
            for k in r:
                if isinstance(r[k], str):
                    r[k] = float(r[k])

        obj = cls(clock_view)
        obj._history = history
        return obj
