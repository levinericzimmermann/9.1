import abc
import dataclasses

import ranges

from mutwo import core_events


class Column(tuple[str, str, str]):
    ...


class Header(Column):
    def __new__(self, content_name0: str, content_name1: str):
        return super().__new__(tuple, ("player", content_name0, content_name1))


class Content(Column):
    def __new__(self, player_index: int, content0: str, content1: str):
        return super().__new__(tuple, (str(player_index + 1), content0, content1))


class PlayerEvent(core_events.SimpleEvent):
    @property
    @abc.abstractmethod
    def header(self) -> Header:
        ...

    @property
    @abc.abstractmethod
    def content(self) -> Content:
        ...


class EventSequence(PlayerEvent):
    def __init__(
        self,
        *args,
        player_index: int,
        event_count: int,
        event_duration_range: ranges.Range,
        **kwargs,
    ):
        self.player_index = player_index
        self.event_count = event_count
        self.event_duration_range = event_duration_range
        super().__init__(
            *args,
            duration=event_duration_range.end
            if event_duration_range.end != float("inf")
            else 10000000000,
            **kwargs,
        )

    @property
    def header(self) -> Header:
        return Header("number of events", "event sequence duration range")

    @property
    def content(self) -> Content:
        def parse_time(time: float) -> str:
            if time == float("inf"):
                parsed_time = r"$\infty$"
            else:
                parsed_time = f"{time}{{\\footnotesize s}}"

            # return f"{parsed_time}{{\\footnotesize s}}"
            return f"{parsed_time}"

        def get_time_range():
            start_time, stop_time = (
                self.event_duration_range.start,
                self.event_duration_range.end,
            )

            start, stop = (parse_time(time) for time in (start_time, stop_time))

            # if start_time == 0 and stop_time == float("inf"):
            #     return f"\dots until {stop}"

            return f"{start} -- {stop}"

        return Content(
            self.player_index,
            str(self.event_count),
            get_time_range(),
        )


class Page(
    core_events.SimultaneousEvent[PlayerEvent],
    class_specific_side_attribute_tuple=("page_number",),
):
    def __init__(self, *args, page_number: int, **kwargs):
        self.page_number = page_number
        super().__init__(*args, **kwargs)
