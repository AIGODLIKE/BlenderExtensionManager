import json
from typing import Union, Optional, Callable
from pathlib import Path
from translation import _p
from nicegui import ui
from model.config import Config


def get_b3d_ext_dir() -> Path:
    config = Config()
    version = config.data.get('blender_version', '4.2')
    return Path.home().joinpath('AppData', 'Roaming', 'Blender Foundation', 'Blender', version, 'extensions')


def get_b3d_local_repos() -> tuple[bool, Union[dict[str, Path], None, str]]:
    """

    :param version:
    :return:
        bool: True if success
        ui.element or dict '{repo_name:index_file}'
    """
    d = get_b3d_ext_dir()
    if not d.exists():
        return False, None

    repo_index_file = dict()

    for directory in d.iterdir():
        if not directory.is_dir(): continue
        is_local_repo = False
        for subdir in directory.iterdir():
            if subdir.name != '.blender_ext': continue
            bl_ext_repo_file = subdir.joinpath('bl_ext_repo.json')
            try:
                with open(bl_ext_repo_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    ext_list = data.get('data', [])
                    if len(ext_list) == 0: is_local_repo = True
            except FileNotFoundError:
                return False, None
            except Exception as e:
                return False, str(e)
        if is_local_repo:
            repo_index_file[directory.name] = directory.joinpath('.blender_ext', 'index.json')

    return True, repo_index_file


def parse_repo_index_file(fp: Path, version: str = 'v1') -> Union[list[dict], None]:
    with open(fp, mode='r', encoding='utf-8') as f:
        json_data = json.load(f)
        v = json_data.get('version')
        if v != version: return None
        d = json_data.get('data')
        return d


def backup_repo_index(repo_name: str) -> tuple[bool, str]:
    import time, shutil

    fp = get_b3d_ext_dir().joinpath(repo_name, '.blender_ext', 'index.json')
    if not fp.exists(): return (False, f'file not exists: {str(fp)}')
    backup_dir = get_b3d_ext_dir().joinpath(repo_name, '.blender_ext_backup')
    if not backup_dir.exists():
        backup_dir.mkdir(parents=True)
    time_str = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())
    backup_fp = backup_dir.joinpath('index.json' + f'_{time_str}_bak')
    try:
        shutil.copy(fp, backup_fp)
    except PermissionError:
        return (False, f'{_p("Backup failed")}: {str(backup_fp)}')
    return (True, f'Backup success: {str(backup_fp)}')


def write_repo_index(repo_name: str, data_list: list[str]) -> tuple[bool, str]:
    # backup dir
    res, msg = backup_repo_index(repo_name)
    if not res: return (res, msg)

    import json
    fp = get_b3d_ext_dir().joinpath(repo_name, '.blender_ext', 'index.json')
    with open(fp, 'r', encoding='utf-8') as f:
        ori_data = json.load(f)
    ori_data['data'] = data_list

    try:
        with open(fp, 'w', encoding='utf-8') as f:
            json.dump(ori_data, f, ensure_ascii=False, indent=4)
    except:
        return (False, f'write failed: {str(fp)}')

    return (True, f'write success: {str(fp)}')


def write_repo_index_with_id(repo_name: str, data: dict) -> tuple[bool, str]:
    # backup dir
    res, msg = backup_repo_index(repo_name)
    if not res: return (res, msg)

    import json
    fp = get_b3d_ext_dir().joinpath(repo_name, '.blender_ext', 'index.json')
    with open(fp, 'r', encoding='utf-8') as f:
        ori_data = json.load(f)

    data_list: list = ori_data.get('data')
    replace = False
    for i, d in enumerate(data_list):
        if d.get('id') == data.get('id'):
            data_list[i] = data
            replace = True
    if not replace:
        data_list.append(data)
    ori_data['data'] = data_list

    try:
        with open(fp, 'w', encoding='utf-8') as f:
            json.dump(ori_data, f, ensure_ascii=False, indent=4)
    except:
        return (False, f'write failed: {str(fp)}')

    return (True, f'write success: {str(fp)}')


def remove_repo_index_by_id(repo_name: str, id: str) -> tuple[bool, str]:
    fp = get_b3d_ext_dir().joinpath(repo_name, '.blender_ext', 'index.json')
    with open(fp, 'r', encoding='utf-8') as f:
        ori_data = json.load(f)
    data_list: list = ori_data.get('data')
    for i, d in enumerate(data_list):
        if d.get('id') == id:
            data_list.pop(i)
            break
    try:
        with open(fp, 'w', encoding='utf-8') as f:
            json.dump(ori_data, f, ensure_ascii=False, indent=4)
    except:
        return (False, f'write failed: {str(fp)}')

    return (True, f'write success: {str(fp)}')
