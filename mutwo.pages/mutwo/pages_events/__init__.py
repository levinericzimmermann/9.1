import dataclasses
import jinja2


class Column(tuple[str, str, str]):
    ...


class Header(Column):
    def __init__(self, content_name0: str, content_name1: str):
        super().__init__(("player", content_name0, content_name1))


class Content(Column):
    def __init__(self, player_index: int, content0: str, content1: str):
        super().__init__((str(player_index), content0, content1))


@dataclasses.dataclass
class PlayerEntry(object):
    header: Header
    content: Content


@dataclasses.dataclass
class Page(object):
    page_number: int
    player_entry_tuple: tuple[PlayerEntry, ...]

    environment = jinja2.Environment(loader=jinja2.FileSystemLoader("./"))

    def export(self):
        template = environment.get_template(jinja2_file_path)
        toml_str = template.render()
