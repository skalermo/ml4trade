import math

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mpl_toolkits.axes_grid1 import make_axes_locatable

from ml4trade.domain.constants import env_history_keys


def render_all(history: dict):
    plt.style.use('ggplot')
    plt.rcParams.update({'font.size': 16})
    fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(16, 16))

    for k in env_history_keys:
        # history[k] = history[k][-24*7-10:-10]
        history[k] = history[k][24:-10]

    _plot_balance(history, axs[0, 0], fig, 'Datetime', 'Zł', 'All-time Profit')
    _plot_battery(history, axs[0, 1], fig, 'Time', '%', 'Last 2 days Battery state')
    _plot_scheduled(history, axs[1, 0], fig, 'Time', 'Zł', 'Last 2 days Scheduled thresholds')
    _plot_unscheduled(history, axs[1, 1], fig, 'Time', 'MWh', 'Last 2 days Unscheduled energy amounts')

    fig.tight_layout()
    plt.show()


def _plot_balance(history: dict, ax, fig, xlabel, ylabel, title):
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.title.set_text(title)

    plt.sca(ax)
    plt.xticks(rotation=45)
    ax.plot(history['datetime'], history['wallet_balance'], color='black')
    ax.legend(loc='upper right')


def _plot_battery(history: dict, ax, fig, xlabel, ylabel, title):
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.title.set_text(title)

    battery_history_last_2_days = history['battery'][-48:]
    datetime_history_last_2_days = history['datetime'][-48:]
    ax.plot(datetime_history_last_2_days, battery_history_last_2_days, color='black')
    ax.legend(loc='upper right')
    hours = mdates.HourLocator(byhour=list(range(0, 24, 4)), interval=1)
    h_fmt = mdates.DateFormatter('%H')
    ax.xaxis.set_major_locator(hours)
    ax.xaxis.set_major_formatter(h_fmt)


def _plot_scheduled(history: dict, ax, fig, xlabel, ylabel, title):
    ax.set_xlabel(xlabel)

    datetime_history_last_2_days = history['datetime'][-48:]
    prices_history_last_2_days = history['price'][-48:]
    buys_last_2_days = history['scheduled_buy_amounts'][-48:]
    sells_last_2_days = history['scheduled_sell_amounts'][-48:]
    buys = list(map(lambda x: float(x[0]), buys_last_2_days))
    sells = list(map(lambda x: float(x[0]), sells_last_2_days))

    divider = make_axes_locatable(ax)
    ax2 = divider.new_vertical(size="400%", pad=0.1)
    fig.add_axes(ax2)
    ax2.set_ylabel(ylabel)
    ax2.title.set_text(title)

    ax.plot(datetime_history_last_2_days, buys, color='red')
    ax.plot(datetime_history_last_2_days, sells, color='blue')
    ax.set_ylim(0, 5)
    ax.spines['top'].set_visible(False)

    ax2.plot(datetime_history_last_2_days, prices_history_last_2_days, color='black', label='market price')
    ax2.plot(datetime_history_last_2_days, buys, color='red', label='buy threshold')
    ax2.plot(datetime_history_last_2_days, sells, color='blue', label='sell threshold')
    ax2.legend(loc='upper right')
    ax2.set_ylim(50, 200)
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


def _plot_unscheduled(history: dict, ax, fig, xlabel, ylabel, title):
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.title.set_text(title)

    datetime_history_last_2_days = history['datetime'][-48:]
    buys_last_2_days = history['unscheduled_buy_amounts'][-48:]
    sells_last_2_days = history['unscheduled_sell_amounts'][-48:]
    buys = list(map(lambda x: float(x[0]), buys_last_2_days))
    sells = list(map(lambda x: float(x[0]), sells_last_2_days))

    ax.plot(datetime_history_last_2_days, buys, color='red', label='buy amount')
    ax.plot(datetime_history_last_2_days, sells, color='blue', label='sell amount')
    ax.legend(loc='upper right')

    hours = mdates.HourLocator(byhour=list(range(0, 24, 4)), interval=1)
    h_fmt = mdates.DateFormatter('%H')
    ax.xaxis.set_major_locator(hours)
    ax.xaxis.set_major_formatter(h_fmt)


if __name__ == '__main__':
    import json
    from datetime import datetime

    history_file = '../../env_history.json'
    with open(history_file, 'r') as f:
        _history = json.load(f)

    _history['datetime'] = list(map(datetime.fromisoformat, _history['datetime']))
    _history['battery'] = list(map(lambda x: x * 100, _history['battery']))
    render_all(_history)
