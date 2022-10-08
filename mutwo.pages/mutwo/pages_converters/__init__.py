import abc
import dataclasses
import os
import subprocess
import typing

import numpy as np
import jinja2
import ranges

from mutwo import core_converters
from mutwo import core_events
from mutwo import core_utilities
from mutwo import pages_constants
from mutwo import pages_events
from mutwo import pages_generators

from . import constants

Header = tuple[str, str, str]
Content = tuple[str, str, str]


class PageToPlayerDataList(core_converters.abc.Converter):
    def convert(
        self, page_to_convert: pages_events.Page
    ) -> list[tuple[Header, Content]]:
        player_data_list = []
        for page_event in page_to_convert:
            player_data_list.append((page_event.header, page_event.content))
        return player_data_list


class Jinja2Converter(core_converters.abc.Converter):
    def __init__(self, template_path: str):
        environment = jinja2.Environment(loader=jinja2.FileSystemLoader("./"))
        self.template = environment.get_template(template_path)

    @abc.abstractmethod
    def _get_default_path(self, *args, **kwargs) -> str:
        ...

    @abc.abstractmethod
    def _get_tex_file_content(self, *args, **kwargs) -> str:
        ...

    def convert(
        self, *args, path: typing.Optional[str] = None, cleanup: bool = True, **kwargs
    ) -> str:
        if path is None:
            path = self._get_default_path(*args, **kwargs)
        tex_path = f"{path}.tex"
        aux_path = f"{path}.aux"
        log_path = f"{path}.log"
        tex_file_content = self._get_tex_file_content(*args, **kwargs)
        with open(tex_path, "w") as tex_file:
            tex_file.write(tex_file_content)
        subprocess.call(
            ["lualatex", "--output-directory=builds/", "--output-format=pdf", tex_path]
        )
        if cleanup:
            os.remove(tex_path)
            os.remove(aux_path)
            os.remove(log_path)
        return f"{path}.pdf"


class PageToPDF(Jinja2Converter):
    def __init__(self):
        super().__init__(constants.PAGE_TEMPLATE_PATH)
        self.page_to_player_data_list = PageToPlayerDataList()

    def _get_default_path(self, page_to_convert: pages_events.Page, **kwargs) -> str:
        voice_count = len(page_to_convert)
        return f"{constants.BUILD_PATH}/{voice_count}_{page_to_convert.page_number}"

    def _get_tex_file_content(
        self, page_to_convert: pages_events.Page, **kwargs
    ) -> str:
        player_data_list = self.page_to_player_data_list.convert(page_to_convert)
        tex_file_content = self.template.render(
            player_data_list=player_data_list, page_number=page_to_convert.page_number
        )
        return tex_file_content


class PageSequentialEventToPDF(core_converters.abc.Converter):
    def __init__(self):
        self.page_to_pdf = PageToPDF()

    def convert(
        self,
        page_sequential_event_to_convert: core_events.SequentialEvent[
            pages_events.Page
        ],
        path: typing.Optional[str] = None,
        cleanup: bool = True,
    ) -> str:
        voice_count = len(page_sequential_event_to_convert[0])
        if path is None:
            path = f"{constants.BUILD_PATH}/score_{voice_count}_players.pdf"
        path_list = [
            self.page_to_pdf.convert(page, cleanup=cleanup)
            for page in page_sequential_event_to_convert
        ]
        subprocess.call(["pdftk"] + path_list + ["output", path])
        if cleanup:
            for path in path_list:
                os.remove(path)
        return path


class XToPageSequentialEvent(core_converters.abc.Converter):
    def __init__(
        self,
        minima_duration_generator: pages_generators.EnvelopeDistributionRandom,
        maxima_duration_generator: pages_generators.EnvelopeDistributionRandom,
        minima_event_count: int = 0,
        maxima_event_count: int = 5,
        maxima_event_count_envelope: core_events.Envelope = core_events.Envelope(
            [[0, 5], [0.2, 2], [0.4, 8], [0.6, 0], [0.8, 9], [1, 3]]
        ),
        random_seed: int = 1000,
    ):
        self.minima_duration_generator = minima_duration_generator
        self.maxima_duration_generator = maxima_duration_generator
        self.minima_event_count = minima_event_count
        self.maxima_event_count = maxima_event_count
        self.maxima_event_count_envelope = maxima_event_count_envelope
        self.random = np.random.default_rng(seed=random_seed)

    def _get_event_count_tuple(
        self, voice_count: int, page_index: int, page_count: int
    ) -> tuple[int, ...]:
        position = page_index / page_count
        maxima_event_count = self.maxima_event_count_envelope.value_at(position)
        event_count_list = None
        while event_count_list is None or sum(event_count_list) > maxima_event_count:
            event_count_list = [
                self.random.integers(
                    self.minima_event_count, self.maxima_event_count, dtype=int
                )
                for _ in range(voice_count)
            ]
        return tuple(event_count_list)

    def _get_duration_range(self, event_count: int) -> ranges.Range:
        # In case there is no event, this 'no-event-rest' should
        # still have a certain duration. Therefore we "betray" the algorithm
        # by "faking" to have a higher event_count than reality.
        if event_count == 0:
            event_count = self.random.integers(1, 3)

        minima_list, maxima_list = [], []
        for _ in range(event_count):
            for list_, generator in (
                (minima_list, self.minima_duration_generator),
                (maxima_list, self.maxima_duration_generator),
            ):
                list_.append(generator())

        minima, maxima = (
            # Take average from given list.
            # Only give values by 5 steps.
            5 * round(np.average(list_) / 5)
            for list_ in (minima_list, maxima_list)
        )

        # For unlikely case if maxima is higher than minima
        if maxima <= minima:
            maxima = minima + 5

        return ranges.Range(minima, maxima)

    def convert(
        self, page_count: int = 100, voice_count: int = 4
    ) -> core_events.SequentialEvent[pages_events.Page]:
        page_sequential_event = core_events.SequentialEvent([])
        for page_number in range(page_count):
            page = pages_events.Page(page_number=page_number)
            event_count_tuple = self._get_event_count_tuple(
                voice_count, page_number, page_count
            )
            for voice_index, event_count in enumerate(event_count_tuple):
                duration_range = self._get_duration_range(event_count)
                event_sequence = pages_events.EventSequence(
                    player_index=voice_index,
                    event_count=event_count,
                    event_duration_range=duration_range,
                )
                page.append(event_sequence)
            page_sequential_event.append(page)
        return page_sequential_event


class XToScore(Jinja2Converter):
    @dataclasses.dataclass
    class GroupDivision(object):
        group_size: int

        @property
        def division(self) -> str:
            division_latex_list = []
            for division in core_utilities.find_numbers_which_sums_up_to(
                self.group_size, constants.PARTY_COUNT_TUPLE
            ):
                if len(division) == 1:
                    division_latex = str(division[0])
                else:
                    division_latex = "${}$".format("+".join(tuple(map(str, division))))
                division_latex_list.append(division_latex)
            return " or ".join(division_latex_list)

    def _get_group_division_table(
        self, minima_group_size: int = 3, maxima_group_size: int = 17
    ) -> tuple[tuple[str, str, str, str], ...]:
        group_division_list = [
            self.GroupDivision(group_size)
            for group_size in range(minima_group_size, maxima_group_size)
        ]
        group_division_count = len(group_division_list)
        assert group_division_count % 2 == 0
        group_division_table = []
        for group_division_pair in zip(
            group_division_list, group_division_list[int(group_division_count / 2) :]
        ):
            group_division_table_entry = []
            for group_division in group_division_pair:
                group_division_table_entry.append(str(group_division.group_size))
                group_division_table_entry.append(group_division.division)
            group_division_table.append(tuple(group_division_table_entry))
        return tuple(group_division_table)

    def __init__(self):
        super().__init__(constants.SCORE_TEMPLATE_PATH)

    def _get_default_path(self, *args, **kwargs) -> str:
        return f"{constants.BUILD_PATH}/score"

    def _get_tex_file_content(self, *args, **kwargs) -> str:
        return self.template.render(
            title=pages_constants.TITLE, division_table=self._get_group_division_table()
        )
