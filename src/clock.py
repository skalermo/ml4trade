from datetime import datetime, timedelta


_cur_datetime: datetime
_cur_tick: int
_tick_length: timedelta


def init(start_datetime: datetime, start_tick: int = 0, tick_length: timedelta = timedelta(hours=1)):
    global _cur_datetime, _cur_tick, _tick_length
    _cur_datetime = start_datetime
    _cur_tick = start_tick
    _tick_length = tick_length


def tick(times: int = 1):
    global _cur_tick, _cur_datetime
    _cur_tick += times
    _cur_datetime += _tick_length * times


def cur_datetime():
    return _cur_datetime


def cur_tick():
    return _cur_tick
