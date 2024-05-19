import re
from pathlib import Path
from nicegui import ui
from typing import Union

from model.schema import Schema
from view_model.widget_ext_card import ExtensionCard
from public_path import get_b3d_ext_dir, get_b3d_local_repos


def parse_repo_index_file(fp: Path, version: str = 'v1') -> Union[list[dict], None]:
    import json
    with open(fp, mode='r', encoding='utf-8') as f:
        json_data = json.load(f)
        v = json_data.get('version')
        if v != version: return None
        d = json_data.get('data')
        return d


def backup_repo_index(repo_name: str, version: str = '4.2') -> tuple[bool, str]:
    import time, shutil
    fp = get_b3d_ext_dir(version).joinpath(repo_name, '.blender_ext', 'index.json')
    if not fp.exists(): return (False, f'file not exists: {str(fp)}')
    backup_dir = get_b3d_ext_dir().joinpath(repo_name, '.blender_ext_backup')
    if not backup_dir.exists():
        backup_dir.mkdir(parents=True)
    time_str = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())
    backup_fp = backup_dir.joinpath('index.json' + f'_{time_str}_bak')
    try:
        shutil.copy(fp, backup_fp)
    except:
        return (False, f'backup failed: {str(backup_fp)}')
    return (True, f'backup success: {str(backup_fp)}')


def write_repo_index(repo_name: str, data_list: list[str], version: str = '4.2') -> tuple[bool, str]:
    # backup dir
    res, msg = backup_repo_index(repo_name)
    if not res: return (res, msg)

    import json
    fp = get_b3d_ext_dir(version).joinpath(repo_name, '.blender_ext', 'index.json')
    with open(fp, 'r', encoding='utf-8') as f:
        ori_data = json.load(f)
    ori_data['data'] = data_list

    try:
        with open(fp, 'w', encoding='utf-8') as f:
            json.dump(ori_data, f, ensure_ascii=False, indent=4)
    except:
        return (False, f'write failed: {str(fp)}')

    return (True, f'write success: {str(fp)}')


# def search_filter(search_list: list, query_word: str):
#     import difflib
#     res = difflib.get_close_matches(query_word, search_list, cutoff=0.5)
#
#     return res


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
