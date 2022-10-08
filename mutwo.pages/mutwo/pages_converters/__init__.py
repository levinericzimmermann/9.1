import os
import subprocess
import random
import typing

import jinja2
import ranges

from mutwo import core_converters
from mutwo import core_events
from mutwo import pages_events

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


class PageToPDF(core_converters.abc.Converter):
    def __init__(self):
        environment = jinja2.Environment(loader=jinja2.FileSystemLoader("./"))
        self.template = environment.get_template(constants.PAGE_TEMPLATE_PATH)
        self.page_to_player_data_list = PageToPlayerDataList()

    def convert(
        self,
        page_to_convert: pages_events.Page,
        path: typing.Optional[str] = None,
        cleanup: bool = True,
    ) -> str:
        voice_count = len(page_to_convert)
        if path is None:
            path = f"{constants.BUILD_PATH}/{voice_count}_{page_to_convert.page_number}"
        tex_path = f"{path}.tex"
        aux_path = f"{path}.aux"
        log_path = f"{path}.log"
        player_data_list = self.page_to_player_data_list.convert(page_to_convert)
        tex_file_content = self.template.render(
            player_data_list=player_data_list, page_number=page_to_convert.page_number
        )
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
    def convert(
        self, page_count: int = 100, voice_count: int = 4
    ) -> core_events.SequentialEvent[pages_events.Page]:
        page_sequential_event = core_events.SequentialEvent([])
        for page_number in range(page_count):
            page = pages_events.Page(page_number=page_number)
            for voice_index in range(voice_count):
                event_count = int(random.uniform(0, 5))
                duration_range = ranges.Range(
                    int(random.uniform(1, 10)), int(random.uniform(15, 20))
                )
                event_sequence = pages_events.EventSequence(
                    player_index=voice_index,
                    event_count=event_count,
                    event_duration_range=duration_range,
                )
                page.append(event_sequence)
            page_sequential_event.append(page)
        return page_sequential_event
