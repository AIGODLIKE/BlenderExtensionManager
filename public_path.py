import os
import json
from pathlib import Path
from typing import Union


def get_b3d_ext_dir(version: str = '4.2') -> Path:
    return Path.home().joinpath('AppData', 'Roaming', 'Blender Foundation', 'Blender', version, 'extensions')


def get_b3d_local_repos(version: str = '4.2') -> Union[dict[str, Path], None]:
    """

    :param version:
    :return:
        dict '{repo_name:index_file}'
    """
    d = get_b3d_ext_dir(version)
    if not d.exists(): return

    repo_index_file = dict()

    for directory in d.iterdir():
        if not directory.is_dir(): continue
        is_local_repo = False
        for subdir in directory.iterdir():
            if subdir.name != '.blender_ext': continue
            bl_ext_repo_file = subdir.joinpath('bl_ext_repo.json')
            with open(bl_ext_repo_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                ext_list = data.get('data', [])
                if len(ext_list) == 0: is_local_repo = True
        if is_local_repo:
            repo_index_file[directory.name] = directory.joinpath('.blender_ext', 'index.json')

    return repo_index_file
