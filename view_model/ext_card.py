from pathlib import Path
from nicegui import ui
from typing import Union

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


def write_repo_index_file(repo_name, ori_id: str, data: dict):
    import json, time, shutil
    fp = get_b3d_ext_dir().joinpath(repo_name, '.blender_ext', 'index.json')
    backup_dir = get_b3d_ext_dir().joinpath(repo_name, '.blender_ext_backup')
    if not backup_dir.exists():
        backup_dir.mkdir(parents=True)
    time_str = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())
    backup_fp = backup_dir.joinpath('index.json' + f'_{time_str}_bak')
    shutil.copy(fp, backup_fp)
    # read original data
    with open(fp, 'r', encoding='utf-8') as f:
        ori_data = json.load(f)

    exts_data = ori_data.get('data')
    for d in exts_data:
        if d.get('id') == ori_id:
            d.update(data)
            break
    ori_data['data'] = exts_data
    with open(fp, 'w', encoding='utf-8') as f:
        json.dump(ori_data, f, ensure_ascii=False, indent=4)


def open_file(repo_name: str, id: str):
    """open explorer or finder"""
    import sys, os
    fp = get_b3d_ext_dir().joinpath(repo_name, id)
    if sys.platform == 'win32':
        os.startfile(fp)
    else:
        ui.notify(f'Platform not support yet', type='negative')


def draw_all_cards(repo: str):
    name_index = get_b3d_local_repos(version='4.2')
    index_file = name_index.get(repo, None)
    datas = parse_repo_index_file(index_file)
    for d in datas:
        with ExtensionCard(d).classes('w-full shadow-1').tight() as card:
            card.repo_name = repo
