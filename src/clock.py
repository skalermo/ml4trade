from datetime import datetime, time, timedelta


class Clock:
    def __init__(self, start_datetime: datetime,
                 start_tick: int = 0, tick_duration: timedelta = timedelta(hours=1)):
        self.cur_datetime = start_datetime
        self.cur_tick = start_tick
        self.tick_duration = tick_duration

    def tick(self) -> None:
        self.cur_tick += 1
        self.cur_datetime += self.tick_duration

    def is_it_time(self, time_to_check: time) -> bool:
        return self.cur_datetime.time() == time_to_check
