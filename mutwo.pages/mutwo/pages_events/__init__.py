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
        **kwargs
    ):
        self.player_index = player_index
        self.event_count = event_count
        self.event_duration_range = event_duration_range
        super().__init__(*args, duration=event_duration_range.end, **kwargs)

    @property
    def header(self) -> Header:
        return Header("number of events", "event sequence duration range")

    @property
    def content(self) -> Content:
        return Content(
            self.player_index,
            str(self.event_count),
            f"{self.event_duration_range.start}s -- {self.event_duration_range.end}s",
        )


class Page(
    core_events.SimultaneousEvent[PlayerEvent],
    class_specific_side_attribute_tuple=("page_number",),
):
    def __init__(self, *args, page_number: int, **kwargs):
        self.page_number = page_number
        super().__init__(*args, **kwargs)
