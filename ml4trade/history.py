import json
from datetime import datetime
from typing import List, Tuple, Optional

import numpy as np

from ml4trade.domain.clock import ClockView
from ml4trade.domain.consumption import ConsumptionSystem
from ml4trade.domain.market import EnergyMarket, UNSCHEDULED_MULTIPLIER
from ml4trade.domain.production import ProductionSystem
from ml4trade.domain.prosumer import Prosumer

tick_history_keys = [
    'tick', 'datetime',
    'energy_produced', 'energy_consumed', 'battery',
    'price', 'wallet_balance',
    'scheduled_buy_amounts', 'scheduled_sell_amounts',
    'unscheduled_buy_amounts', 'unscheduled_sell_amounts',
]

step_history_keys = [
    'step_tick', 'step_datetime',
    'balance_diff', 'potential_profit',
    'unscheduled_sell_actions_profit', 'unscheduled_buy_actions_loss',
    'action', 'reward',
]


class History:
    def __init__(self, clock_view: ClockView):
        self._clock_view = clock_view
        self._history = {key: [] for key in tick_history_keys + step_history_keys}

    def __getitem__(self, item):
        return self._history[item]

    def tick_update(
            self,
            prosumer: Prosumer,
            market: EnergyMarket,
            production_system: ProductionSystem,
            consumption_system: ConsumptionSystem,
    ):
        self._history['tick'].append(self._clock_view.cur_tick())
        self._history['datetime'].append(self._clock_view.cur_datetime())
        self._history['wallet_balance'].append(prosumer.wallet.balance.value)
        # does not require checking against None
        # because it is being overwritten on every tick
        self._history['scheduled_buy_amounts'].append(prosumer.last_scheduled_buy_transaction)
        self._history['scheduled_sell_amounts'].append(prosumer.last_scheduled_sell_transaction)
        self._history['battery'].append(prosumer.battery.rel_current_charge)
        self._history['unscheduled_buy_amounts'].append(prosumer.last_unscheduled_buy_transaction or (0, False))
        self._history['unscheduled_sell_amounts'].append(prosumer.last_unscheduled_sell_transaction or (0, False))
        self._history['price'].append(market.ds.last_processed)
        self._history['energy_produced'].append(production_system.ds.last_processed)
        self._history['energy_consumed'].append(consumption_system.ds.last_processed)
        prosumer.last_unscheduled_buy_transaction = None
        prosumer.last_unscheduled_sell_transaction = None

    def step_update(self, action: np.ndarray, balance_diff: float):
        self._history['step_tick'].append(self._clock_view.cur_tick())
        self._history['step_datetime'].append(self._clock_view.cur_datetime())
        self._history['action'].append(action.tolist())
        self._history['balance_diff'].append(balance_diff)

        (
            potential_profit,
            unscheduled_sell_actions_profit,
            unscheduled_buy_actions_loss,
        ) = self._last_day_summary()

        self._history['potential_profit'].append(potential_profit)
        self._history['unscheduled_sell_actions_profit'].append(unscheduled_sell_actions_profit)
        self._history['unscheduled_buy_actions_loss'].append(unscheduled_buy_actions_loss)

    def save_reward(self, reward: float):
        self._history['reward'].append(reward)

    def last_day_potential_profit(self) -> float:
        return self._item_from_last_day_summary('potential_profit')

    def last_day_unscheduled_sell_profit(self):
        return self._item_from_last_day_summary('unscheduled_sell_actions_profit')

    def last_day_unscheduled_buy_loss(self):
        return self._item_from_last_day_summary('unscheduled_buy_actions_loss')

    def _item_from_last_day_summary(self, item: str):
        if not self._history['step_tick']:
            return 0
        if self._history['step_tick'][-1] <= self._clock_view.cur_tick():
            return self._history[item][-1]
        summary = self._last_day_summary()
        return {
            'potential_profit': summary[0],
            'unscheduled_sell_actions_profit': summary[1],
            'unscheduled_buy_actions_loss': summary[2],
        }[item]

    def _last_day_summary(self) -> Tuple[float, float, float]:
        # max amount of time history goes unfilled is
        # 24 - scheduling_hour hours and another 24 hours
        # we need another 24 hours to fill up history
        # with real values
        if len(self._history['tick']) < 72 - self._clock_view.scheduling_hour():
            return 0, 0, 0

        start_idx = -self._clock_view.cur_datetime().hour - 24
        end_idx = start_idx + 24 or None

        avg_price = sum(self._history['price'][start_idx:end_idx]) / 24

        total_energy_produced = sum(self._history['energy_produced'][start_idx:end_idx])
        total_energy_consumed = sum(self._history['energy_consumed'][start_idx:end_idx])
        potential_profit = (total_energy_produced - total_energy_consumed) * avg_price

        def sum_unscheduled_amounts(a: List[Tuple[float, bool]]) -> float:
            return sum(map(lambda x: x[0], filter(lambda x: x[1], a)), 0)

        bought = self._history['unscheduled_buy_amounts'][start_idx:end_idx]
        sold = self._history['unscheduled_sell_amounts'][start_idx:end_idx]
        total_bought = sum_unscheduled_amounts(bought)
        total_sold = sum_unscheduled_amounts(sold)
        unscheduled_sell_actions_profit = total_sold * avg_price / UNSCHEDULED_MULTIPLIER
        unscheduled_buy_actions_loss = total_bought * avg_price * UNSCHEDULED_MULTIPLIER

        return potential_profit, unscheduled_sell_actions_profit, unscheduled_buy_actions_loss

    def remove_last_tick_entries(self, n: int):
        for key in tick_history_keys:
            self._history[key] = self._history[key][:-n or None]

    def render(self):
        from ml4trade.rendering.charts import render_all
        render_all(self._history)

    def save(self, path: str = 'env_history.json'):
        with open(path, 'w') as f:
            json.dump(self._history, f, indent=2, default=str)

    @classmethod
    def load(cls, path: str, clock_view: Optional[ClockView] = None) -> 'History':
        with open(path, 'r') as f:
            history = json.load(f)

        history['datetime'] = list(map(datetime.fromisoformat, history['datetime']))

        obj = cls(clock_view)
        obj._history = history
        return obj
