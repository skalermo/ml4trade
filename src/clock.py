from datetime import datetime, time, timedelta


from src.constants import START_TIME, SCHEDULING_TIME, ACTION_REPLACEMENT_TIME


class ClockView:
    def __init__(self, clock: 'SimulationClock'):
        self._clock = clock

    def cur_datetime(self) -> datetime:
        return self._clock.cur_datetime

    def cur_tick(self) -> int:
        return self._clock.cur_tick


class SimulationClock:
    def __init__(self, start_datetime: datetime = START_TIME,
                 scheduling_time: time = SCHEDULING_TIME, action_replacement_time: time = ACTION_REPLACEMENT_TIME,
                 start_tick: int = 0, tick_duration: timedelta = timedelta(hours=1)):
        self.cur_datetime = start_datetime
        self.scheduling_time = scheduling_time
        self.action_replacement_time = action_replacement_time
        self.cur_tick = start_tick
        self.tick_duration = tick_duration

    def tick(self) -> None:
        self.cur_tick += 1
        self.cur_datetime += self.tick_duration

    def is_it_scheduling_hour(self) -> bool:
        return self.scheduling_time.hour == self.cur_datetime.hour

    def is_it_action_replacement_hour(self) -> bool:
        return self.action_replacement_time.hour == self.cur_datetime.hour

    def view(self) -> ClockView:
        return ClockView(self)
