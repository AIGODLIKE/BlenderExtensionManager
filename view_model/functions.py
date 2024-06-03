import json
from typing import Union, Optional, Callable
from pathlib import Path
from translation import _p
from nicegui import ui, app


def get_b3d_ext_dir() -> Path:
    version = app.storage.general.get("blender_version", '4.2')
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
                is_local_repo = True
            except Exception as e:
                return False, str(e)
        if is_local_repo:
            repo_index_file[directory.name] = directory.joinpath('.blender_ext', 'index.json')

    return True, repo_index_file


def parse_repo_index_file(fp: Path, version: str = 'v1') -> Union[list[dict], None]:
    if not fp or not fp.exists(): return None
    with open(fp, mode='r', encoding='utf-8') as f:
        json_data = json.load(f)
        v = json_data.get('version')
        if v != version: return None
        d = json_data.get('data')
        return d


def get_repos_data(repo_name: str) -> list[dict]:
    res, repos = get_b3d_local_repos()
    if not res:
        return []
    index_file = repos.get(repo_name, None)
    if not index_file:
        return []

    data = parse_repo_index_file(index_file)
    if data is None:
        return []
    return data


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


def write_repo_index(repo_name: str, data_list: list[dict]) -> tuple[bool, str]:
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


def build_addon_zip_file(zip_dir: Path, dest_zip_path: Path, fix_name_id: str = None) -> tuple[bool, str]:
    """
    :param zip_dir:
    :param dest_zip_path: output zip filepath
    :param fix_name_id: use id to name sub_dir_instead of name
    :return:
        bool: success
        str: dest_zip_path/err_msg
    """
    import shutil, os
    import zipfile

    def prepare_files():
        temp_dir = dest_zip_path.parent.joinpath('BEM_TMP_ZIP')
        if fix_name_id:
            sub_dir = temp_dir.joinpath(fix_name_id)
        else:
            sub_dir = temp_dir.joinpath(dest_zip_path.stem)
        if sub_dir.exists():
            shutil.rmtree(sub_dir)
        sub_dir.mkdir(parents=True)

        for file in zip_dir.glob('*'):
            if file.is_dir():
                if file.name.startswith('__') or file.name.startswith('.'): continue
                shutil.copytree(file, sub_dir.joinpath(file.name))

            elif file.is_file():
                if file.name == __file__: continue

                shutil.copy(file, sub_dir.joinpath(file.name))

        return temp_dir

    try:
        temp_dir = prepare_files()
        with zipfile.ZipFile(dest_zip_path, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as zip:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    zip.write(os.path.join(root, file),
                              arcname=os.path.join(root, file).replace(str(temp_dir), ''))
        shutil.rmtree(temp_dir)

        return True, f'{dest_zip_path}'
    except Exception as e:
        return False, str(e)
