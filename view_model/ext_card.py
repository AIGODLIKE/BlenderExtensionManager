import re
from pathlib import Path
from nicegui import ui
from typing import Union

from model.schema import Schema
from view_model.widget_ext_card import ExtensionCard
from view_model.functions import parse_repo_index_file, get_b3d_local_repos, write_repo_index


def draw_all_cards(repo: str, filter: Union[None, str] = None):
    name_index = get_b3d_local_repos(version='4.2')
    index_file = name_index.get(repo, None)
    datas = parse_repo_index_file(index_file)
    if isinstance(datas, type(None)):
        ui.label(f'{repo}:{index_file} error').style('color:red')
        return
    for d in datas:
        if not isinstance(d, dict): continue
        if filter:
            s = Schema.search_list(d)
            if not re.search(filter, str(s), re.I): continue

        with ExtensionCard(d).classes('w-full shadow-1').tight() as card:
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
