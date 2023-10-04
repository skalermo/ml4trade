from datetime import datetime, time, timedelta


class ClockView:
    def __init__(self, clock: 'SimulationClock', use_tick_offset: bool = True):
        self._clock = clock
        self._use_tick_offset = use_tick_offset

    def cur_datetime(self) -> datetime:
        return self._clock.cur_datetime

    def cur_tick(self) -> int:
        return self._clock.cur_tick + self._clock.tick_offset * int(self._use_tick_offset)

    def scheduling_hour(self) -> int:
        return self._clock.scheduling_hour()


class SimulationClock:
    def __init__(self, start_datetime: datetime,
                 scheduling_time: time, action_replacement_time: time,
                 start_tick: int = 0, tick_duration: timedelta = timedelta(hours=1)):
        self.cur_datetime = start_datetime
        self.scheduling_time = scheduling_time
        self.action_replacement_time = action_replacement_time
        self.cur_tick = start_tick
        self.tick_duration = tick_duration
        self.tick_offset = 0

    def tick(self) -> None:
        self.cur_tick += 1
        self.cur_datetime += self.tick_duration

    def scheduling_hour(self) -> int:
        return self.scheduling_time.hour

    def is_it_scheduling_hour(self) -> bool:
        return self.scheduling_time.hour == self.cur_datetime.hour

    def is_it_action_replacement_hour(self) -> bool:
        return self.action_replacement_time.hour == self.cur_datetime.hour

    def view(self, use_tick_offset: bool = True) -> ClockView:
        return ClockView(self, use_tick_offset)
