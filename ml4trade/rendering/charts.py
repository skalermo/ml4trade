import math

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mpl_toolkits.axes_grid1 import make_axes_locatable

from ml4trade.domain.constants import env_history_keys


def render_all(history: dict, last_n_days: int = 2):
    plt.style.use('ggplot')
    plt.rcParams.update({'font.size': 16})
    fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(16, 16))

    for k in env_history_keys:
        # history[k] = history[k][-24*7-10:-10]
        if k not in (
                'action',
                'balance_diff',
                'potential_reward',
        ):
            history[k] = history[k][24:-10]

    _plot_balance(history, axs[0, 0], fig, 'Datetime', 'Zł', 'All-time Profit')
    _plot_battery(history, last_n_days, axs[0, 1], fig, 'Time', '%', 'Last 2 days Battery state')
    _plot_scheduled(history, last_n_days, axs[1, 0], fig, 'Time', 'Zł', 'Last 2 days Scheduled thresholds')
    _plot_unscheduled(history, last_n_days, axs[1, 1], fig, 'Time', 'MWh', 'Last 2 days Unscheduled energy amounts')

    fig.tight_layout()
    plt.show()


def _plot_balance(history: dict, ax, fig, xlabel, ylabel, title):
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.title.set_text(title)

    plt.sca(ax)
    plt.xticks(rotation=45)
    ax.plot(history['datetime'][::24], np.cumsum(history['balance_diff']) + 10000, color='black')
    ax.plot(history['datetime'][::24], np.cumsum(history['potential_reward']) + 10000, color='blue')
    ax.plot(history['datetime'][::24], np.cumsum(history['potential_reward']) / 2 + 10000, color='red')
    ax.legend(loc='upper right')


def _plot_battery(history: dict, last_n_days: int, ax, fig, xlabel, ylabel, title):
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.title.set_text(title)

    battery_history_last_n_days = history['battery'][-24 * last_n_days:]
    datetime_history_last_n_days = history['datetime'][-24 * last_n_days:]
    ax.plot(datetime_history_last_n_days, battery_history_last_n_days, color='black')
    ax.legend(loc='upper right')
    hours = mdates.HourLocator(byhour=list(range(0, 24, 4)), interval=1)
    h_fmt = mdates.DateFormatter('%H')
    ax.xaxis.set_major_locator(hours)
    ax.xaxis.set_major_formatter(h_fmt)


def _plot_scheduled(history: dict, last_n_days: int,  ax, fig, xlabel, ylabel, title):
    ax.set_xlabel(xlabel)

    datetime_history_last_n_days = history['datetime'][-24 * last_n_days:]
    prices_history_last_n_days = history['price'][-24 * last_n_days:]
    actions = history['action']
    buys = [x[48:72] for x in actions]
    sells = [x[72:] for x in actions]
    buys = [item for sublist in buys for item in sublist][-24 * last_n_days:]
    sells = [item for sublist in sells for item in sublist][-24 * last_n_days:]

    divider = make_axes_locatable(ax)
    ax2 = divider.new_vertical(size="400%", pad=0.1)
    fig.add_axes(ax2)
    ax2.set_ylabel(ylabel)
    ax2.title.set_text(title)

    ax.plot(datetime_history_last_n_days, buys, color='red')
    ax.plot(datetime_history_last_n_days, sells, color='blue')
    ax.set_ylim(0, 5)
    ax.spines['top'].set_visible(False)

    ax2.plot(datetime_history_last_n_days, prices_history_last_n_days, color='black', label='market price')
    ax2.plot(datetime_history_last_n_days, buys, color='red', label='buy threshold')
    ax2.plot(datetime_history_last_n_days, sells, color='blue', label='sell threshold')
    ax2.legend(loc='upper right')
    ax2.set_ylim(min(prices_history_last_n_days) - 20, max(prices_history_last_n_days) + 20)
    ax2.tick_params(bottom=False, labelbottom=False)
    ax2.spines['bottom'].set_visible(False)

    hours = mdates.HourLocator(byhour=list(range(0, 24, 4)), interval=1)
    h_fmt = mdates.DateFormatter('%H')
    ax.xaxis.set_major_locator(hours)
    ax.xaxis.set_major_formatter(h_fmt)
    ax2.xaxis.set_major_locator(hours)
    ax2.xaxis.set_major_formatter(h_fmt)

    def rotate_point(p, angle, o=(0, 0)):
        a = angle / 180 * math.pi
        s = math.sin(a)
        c = math.cos(a)
        x = p[0] - o[0]
        y = p[1] - o[1]
        dx = x * c - y * s
        dy = x * s + y * c
        new_x = dx + o[0]
        new_y = dy + o[1]
        return new_x, new_y

    d = 0.045  # how big to make the diagonal lines in axes coordinates
    # arguments to pass to plot, just so we don't keep repeating them
    kwargs = dict(transform=ax.transAxes, color='k', clip_on=False)
    x1, y1 = rotate_point((-d, 1 - d), 30, (0, 1))
    x2, y2 = rotate_point((+d, 1 + d), 30, (0, 1))
    ax.plot((x1, x2), (y1, y2), **kwargs)  # bottom-left diagonal
    x1, y1 = rotate_point((1 - d, 1 - d), 30, (1, 1))
    x2, y2 = rotate_point((1 + d, 1 + d), 30, (1, 1))
    ax.plot((x1, x2), (y1, y2), **kwargs)  # bottom-right diagonal

    d = 0.015
    kwargs.update(transform=ax2.transAxes)  # switch to the bottom axes
    ax2.plot((-d, +d), (-d, +d), **kwargs)  # top-left diagonal
    ax2.plot((1 - d, 1 + d), (-d, +d), **kwargs)  # top-right diagonal


def _plot_unscheduled(history: dict, last_n_days: int, ax, fig, xlabel, ylabel, title):
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.title.set_text(title)

    datetime_history_last_n_days = history['datetime'][-24 * last_n_days:]
    buys_last_n_days = history['unscheduled_buy_amounts'][-24 * last_n_days:]
    sells_last_n_days = history['unscheduled_sell_amounts'][-24 * last_n_days:]
    buys = list(map(lambda x: float(x[0]), buys_last_n_days))
    sells = list(map(lambda x: float(x[0]), sells_last_n_days))

    ax.plot(datetime_history_last_n_days, buys, color='red', label='buy amount')
    ax.plot(datetime_history_last_n_days, sells, color='blue', label='sell amount')
    ax.legend(loc='upper right')

    hours = mdates.HourLocator(byhour=list(range(0, 24, 4)), interval=1)
    h_fmt = mdates.DateFormatter('%H')
    ax.xaxis.set_major_locator(hours)
    ax.xaxis.set_major_formatter(h_fmt)


if __name__ == '__main__':
    import json
    from datetime import datetime
    import sys

    history_file = '../../env_history.json'
    with open(history_file, 'r') as f:
        _history = json.load(f)

    _history['datetime'] = list(map(datetime.fromisoformat, _history['datetime']))
    _history['battery'] = list(map(lambda x: x * 100, _history['battery']))

    days = sys.argv[1] or 2
    render_all(_history, days)
