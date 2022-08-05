import math
from datetime import timedelta
from typing import List

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mpl_toolkits.axes_grid1 import make_axes_locatable


def _history_to_df(history: List[dict]) -> pd.DataFrame:
    history_df = pd.DataFrame(history)
    history_df.set_index('datetime', inplace=True)
    history_df.sort_index()
    return history_df


def render_all(history: List[dict], last_n_days: int = 2, n_days_offset: int = 0, save_path=None):
    history_df = _history_to_df(history)
    plt.style.use('ggplot')
    plt.rcParams.update({'font.size': 12})
    fig, axs = plt.subplots(nrows=3, ncols=2, figsize=(16, 16))

    _plot_balance(history_df, axs[0, 0], fig, 'Datetime', 'Zł', 'All-time Profit')
    _plot_battery(history_df, last_n_days, n_days_offset, axs[0, 1], fig, 'Time', '', f'Last {last_n_days} days Battery state')
    _plot_scheduled_thresholds(history_df, last_n_days, n_days_offset, axs[1, 0], fig, 'Time', 'Zł', f'Last {last_n_days} days Scheduled thresholds')
    _plot_scheduled_amounts(history_df, last_n_days, n_days_offset, axs[1, 1], fig, 'Time', 'MWh', f'Last {last_n_days} days Scheduled amounts')
    _plot_unscheduled(history_df, last_n_days, n_days_offset, axs[2, 1], fig, 'Time', 'MWh', f'Last {last_n_days} days Unscheduled energy amounts')

    fig.tight_layout()
    if save_path is not None:
        fig.savefig(save_path)
    plt.show()


def _plot_balance(history: pd.DataFrame, ax, fig, xlabel, ylabel, title):
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.sca(ax)
    plt.xticks(rotation=45)

    df = history[history['potential_profit'].notna()]

    ax.plot(df.index, df['wallet_balance'], color='green')
    ax.plot(df.index, np.cumsum(df['potential_profit']), color='blue')
    ax.plot(df.index, np.cumsum(df['potential_profit']) / 2, color='red')
    ax.legend(loc='upper right')
    start_datetime = df.head(1).index.item()
    end_datetime = df.tail(1).index.item()
    ax.title.set_text(f'{title}\n{start_datetime}-{end_datetime}')


def _plot_battery(history: pd.DataFrame, last_n_days: int, n_days_offset: int, ax, fig, xlabel, ylabel, title):
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if last_n_days <= 5:
        hours = mdates.HourLocator(byhour=list(range(0, 24, 4)), interval=1)
        h_fmt = mdates.DateFormatter('%H')
        ax.xaxis.set_major_locator(hours)
        ax.xaxis.set_major_formatter(h_fmt)
    else:
        plt.sca(ax)
        plt.xticks(rotation=45)
    ax.legend(loc='upper right')

    df = history[history['rel_battery'].notna()]
    end_datetime = df.tail(1).index.item() - timedelta(days=n_days_offset)
    start_datetime = end_datetime - timedelta(days=last_n_days)
    ax.title.set_text(f'{title}\n{start_datetime}-{end_datetime}')

    battery_history_last_n_days = df['rel_battery'][start_datetime:end_datetime]
    ax.plot(battery_history_last_n_days.index, battery_history_last_n_days, color='black')


def _plot_scheduled_thresholds(history: pd.DataFrame, last_n_days: int, n_days_offset: int,  ax, fig, xlabel, ylabel, title):
    ax.set_xlabel(xlabel)
    divider = make_axes_locatable(ax)
    ax2 = divider.new_vertical(size="400%", pad=0.1)
    fig.add_axes(ax2)
    ax2.set_ylabel(ylabel)
    ax2.title.set_text(title)
    ax.spines['top'].set_visible(False)
    ax2.legend(loc='upper right')
    ax2.tick_params(bottom=False, labelbottom=False)
    ax2.spines['bottom'].set_visible(False)

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

    df = history[history['price'].notna()]
    end_datetime = df.tail(1).index.item() - timedelta(days=n_days_offset)
    start_datetime = end_datetime - timedelta(days=last_n_days)
    ax2.title.set_text(f'{title}\n{start_datetime}-{end_datetime}')

    prices_history_last_n_days = df['price'][start_datetime:end_datetime]
    buys = df['scheduled_buy_threshold'][start_datetime:end_datetime]
    sells = df['scheduled_sell_threshold'][start_datetime:end_datetime]

    ax.plot(buys.index, buys, color='red')
    ax.plot(sells.index, sells, color='blue')
    ax.set_ylim(0, 5)

    ax2.plot(buys.index, buys, color='red', label='buy threshold')
    ax2.plot(sells.index, sells, color='blue', label='sell threshold')
    ax2.plot(prices_history_last_n_days.index, prices_history_last_n_days, color='black', label='market price')
    ax2.set_ylim(min(prices_history_last_n_days) - 20, max(max(prices_history_last_n_days) + 20), max(buys) + 20, max(sells) + 20)

    if last_n_days <= 5:
        hours = mdates.HourLocator(byhour=list(range(0, 24, 4)), interval=1)
        h_fmt = mdates.DateFormatter('%H')
        ax.xaxis.set_major_locator(hours)
        ax.xaxis.set_major_formatter(h_fmt)
        ax2.xaxis.set_major_locator(hours)
        ax2.xaxis.set_major_formatter(h_fmt)
    else:
        plt.sca(ax)
        plt.xticks(rotation=45)
        plt.sca(ax2)
        plt.xticks(rotation=45)


def _plot_scheduled_amounts(history: pd.DataFrame, last_n_days: int, n_days_offset,  ax, fig, xlabel, ylabel, title):
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(loc='upper right')

    df = history[history['price'].notna()]
    end_datetime = df.tail(1).index.item() - timedelta(days=n_days_offset)
    start_datetime = end_datetime - timedelta(days=last_n_days)
    ax.title.set_text(f'{title}\n{start_datetime}-{end_datetime}')

    energy_produced = df['energy_produced'][start_datetime:end_datetime]
    energy_consumed = df['energy_consumed'][start_datetime:end_datetime]
    energy_diff = energy_produced - energy_consumed
    prices = df['price'][start_datetime:end_datetime]
    buy_amounts = df['scheduled_buy_amount'][start_datetime:end_datetime]
    sell_amounts = df['scheduled_sell_amount'][start_datetime:end_datetime]
    buys_success = df.apply(lambda row: row['scheduled_buy_amount'] if row['scheduled_buy_threshold'] >= row['price'] else 0, axis=1)
    sells_success = df.apply(lambda row: row['scheduled_sell_amount'] if row['scheduled_sell_threshold'] <= row['price'] else 0, axis=1)
    buys_success = buys_success[start_datetime:end_datetime]
    sells_success = sells_success[start_datetime:end_datetime]

    if last_n_days <= 5:
        hours = mdates.HourLocator(byhour=list(range(0, 24, 4)), interval=1)
        h_fmt = mdates.DateFormatter('%H')
        ax.xaxis.set_major_locator(hours)
        ax.xaxis.set_major_formatter(h_fmt)
    else:
        plt.sca(ax)
        plt.xticks(rotation=45)

    ax.plot(prices.index, prices / max(prices) * max(max(buys_success), max(sells_success)), color='gray', label='market price')
    ax.plot(energy_diff.index, energy_diff, color='purple', label='produced - consumed')
    ax.plot(buy_amounts.index, buy_amounts, color='lightsalmon', label='buy amount')
    ax.plot(sell_amounts.index, sell_amounts, color='lightblue', label='sell amount')
    ax.plot(buys_success.index, buys_success, '.', color='red', label='buy amount success')
    ax.plot(sells_success.index, sells_success, '.', color='blue', label='sell amount success')


def _plot_unscheduled(history: pd.DataFrame, last_n_days: int, n_days_offset: int, ax, fig, xlabel, ylabel, title):
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.title.set_text(title)

    df = history[history['unscheduled_buy_amount'].notna()]
    end_datetime = df.tail(1).index.item() - timedelta(days=n_days_offset)
    start_datetime = end_datetime - timedelta(days=last_n_days)
    ax.title.set_text(f'{title}\n{start_datetime}-{end_datetime}')

    buys = df.apply(lambda row: row['unscheduled_buy_amount'][0], axis=1)[start_datetime:end_datetime]
    sells = df.apply(lambda row: row['unscheduled_sell_amount'][0], axis=1)[start_datetime:end_datetime]

    ax.plot(buys.index, buys, color='red', label='buy amount')
    ax.plot(sells.index, sells, color='blue', label='sell amount')
    ax.legend(loc='upper right')

    if last_n_days <= 5:
        hours = mdates.HourLocator(byhour=list(range(0, 24, 4)), interval=1)
        h_fmt = mdates.DateFormatter('%H')
        ax.xaxis.set_major_locator(hours)
        ax.xaxis.set_major_formatter(h_fmt)
    else:
        plt.sca(ax)
        plt.xticks(rotation=45)
