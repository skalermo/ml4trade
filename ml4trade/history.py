import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict

import numpy as np

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

    def __init__(self, clock_view: ClockView):
        self._clock_view = clock_view
        self._tick_offset = clock_view.cur_tick()
        self._history: List[Dict] = []

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
            'price': market.ds.last_processed,
            'wallet_balance': prosumer.wallet.balance.value,
            'rel_battery': prosumer.battery.rel_current_charge,
            'energy_produced': production_system.ds.last_processed,
            'energy_consumed': consumption_system.ds.last_processed,
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
        empty_row = [{}]
        self._history.extend(empty_row * n)

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
            'scheduled_buy_amount': action[h],
            'scheduled_sell_amount': action[24 + h],
            'scheduled_buy_threshold': action[48 + h],
            'scheduled_sell_threshold': action[72 + h],
        } for h in range(24)]

        self._history.extend(actions)

        if self._has_1day_of_history():
            potential_profit = self._last_day_summary()
            self._history[cur_idx - self._clock_view.cur_datetime().hour - 1].update({
                'potential_profit': potential_profit,
            })

    def last_day_potential_profit(self) -> float:
        return self._last_day_summary()

    def _last_day_summary(self) -> float:
        if not self._has_1day_of_history():
            return 0

        end_idx = self._cur_tick_to_idx() - self._clock_view.cur_datetime().hour
        start_idx = end_idx - 24 or None
        last_day_history = self._history[start_idx:end_idx]

        avg_price = sum(r['price'] for r in last_day_history) / 24
        extra_produced = sum(r['energy_produced'] - r['energy_consumed'] for r in last_day_history)
        potential_profit = extra_produced * avg_price

        return potential_profit

    def render(self, last_n_days: int = 2, save_path=None):
        render_all(self._history, last_n_days, save_path)

    def save(self, path: str = 'env_history.json'):
        with open(path, 'w') as f:
            json.dump(self._history, f, indent=2, default=str)

    @classmethod
    def load(cls, path: str, clock_view: Optional[ClockView] = None) -> 'History':
        with open(path, 'r') as f:
            history = json.load(f)

        for r in history:
            r['datetime'] = datetime.fromisoformat(r['datetime'])

        obj = cls(clock_view)
        obj._history = history
        return obj
