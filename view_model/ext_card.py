import re
from pathlib import Path
from nicegui import ui
from typing import Union, Optional

from model.schema import Schema
from view_model.widget_ext_card import ExtensionCard
from view_model.functions import parse_repo_index_file, get_b3d_local_repos, write_repo_index
from translation import _p


def draw_all_cards(repo: str, search_field: Optional[ui.element] = None):
    name_index = get_b3d_local_repos()
    index_file = name_index.get(repo, None)
    datas = parse_repo_index_file(index_file)

    if isinstance(datas, type(None)):
        ui.label(f'{repo}:{index_file} {_p("is empty")}').style('color:red')
        return
    elif len(datas) == 0:
        ui.label(f'{repo}:{index_file} {_p("is empty")}').style('color:red')
        return

    if not isinstance(datas[0], dict):
        ui.label(f'{repo}:{index_file} {_p("file error")}').style('color:red')
        return

    if not search_field:
        for d in datas:
            with ExtensionCard(d).classes('w-full shadow-1').tight() as card:
                card.repo_name = repo
    else:
        filter_str = search_field.value
        search_all = True if "+" in filter_str else False
        for d in datas:
            s = Schema.search_list(d)

            if search_all:
                if not all(re.search(f, str(s), re.I) for f in filter_str.split('+')): continue
            else:
                if not re.search(filter_str, str(s), re.I): continue
            with ExtensionCard(d, search_field=search_field).classes('w-full shadow-1').tight() as card:
                card.repo_name = repo


def save_all_cards(container: Union[ui.row, ui.column, ui.element], repo: str):
    datas = []

    for c in container.default_slot.children:
        if not isinstance(c, ExtensionCard): continue
        datas.append(c.data)

    res, msg = write_repo_index(repo, datas)
    if res:
        ui.notify(f'{repo} saved', type='positive')
    else:
        ui.notify(f'{repo} save failed:\n{msg}', multi_line=True, type='negative')
