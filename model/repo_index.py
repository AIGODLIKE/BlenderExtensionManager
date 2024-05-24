import json
from pathlib import Path
from translation import _p
from typing import Union


# TODO change view_model.function to model.repo_index

class RepoIndexFile():
    def __init__(self, fp: Path):
        self.fp = fp
        self.repo_name: str = self.fp.parent.parent.name
        self.backup_dir: Path = self.fp.parent.parent.joinpath('.blender_ext_backup')
        self.data: dict = self.parse()

    def parse(self, version: str = 'v1') -> Union[dict, None]:
        import json
        fp = self.fp
        with open(fp, mode='r', encoding='utf-8') as f:
            json_data = json.load(f)
            v = json_data.get('version')
            if v != version: return None
            d = json_data.get('data')
            return d

    def reload(self) -> None:
        self.data = self.parse()

    def backup(self) -> tuple[bool, str]:
        """
        backup index file
        :return:
            bool: success
            str: msg
        """
        import time, shutil
        fp = self.fp
        if not fp.exists(): return (False, f'file not exists: {str(fp)}')
        backup_dir = self.backup_dir
        if not backup_dir.exists():
            backup_dir.mkdir(parents=True)
        time_str = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())
        backup_fp = backup_dir.joinpath('index.json' + f'_{time_str}_bak')
        try:
            shutil.copy(fp, backup_fp)
        except PermissionError:
            return (False, f'{_p("Backup failed")}: {str(backup_fp)}')
        return (True, f'Backup success: {str(backup_fp)}')

    def _write_all(self, data_list: list[dict]) -> tuple[bool, str]:
        """
        write all data to index file
        :param data_list:
        :return:
            bool: success
            str: msg
        """
        self.backup()

        import json
        ori_data = self.data
        ori_data['data'] = data_list
        try:
            with open(self.fp, 'w', encoding='utf-8') as f:
                json.dump(ori_data, f, ensure_ascii=False, indent=4)
        except:
            return (False, f'write failed: {str(self.fp)}')
        return (True, f'write success: {str(self.fp)}')

    def save_all(self, data_list: list[dict]) -> tuple[bool, str]:
        return self._write_all(data_list)

    def save_by_id(self, data: dict) -> tuple[bool, str]:
        """
        write  data to index file with id
        :param data_list:
        :return:
            bool: success
            str: msg
        """
        data_list: list = self.data.get('data')
        replace = False
        for i, d in enumerate(data_list):
            if d.get('id') == data.get('id'):
                data_list[i] = data
                replace = True
        if not replace:
            data_list.append(data)
        return self._write_all(data_list)

    def remove_by_id(self, id: str) -> tuple[bool, str]:
        """
        write  data to index file to remove id
        :param data_list:
        :return:
            bool: success
            str: msg
        """
        data_list: list = self.data.get('data')
        for i, d in enumerate(data_list):
            if d.get('id') == id:
                data_list.pop(i)
                break
        return self._write_all(data_list)


class Repos():
    blender_version: str
    index_files: dict[RepoIndexFile]

    def __init__(self, blender_version: '4.2'):
        self.blender_version = blender_version
        res, index_file_dict = self.get_b3d_ext_dir(self.blender_version)
        for repo_name, index_file in index_file_dict.items():
            self.index_files[repo_name] = RepoIndexFile(index_file)

    @staticmethod
    def get_b3d_ext_dir(blender_version: str) -> Path:
        return Path.home().joinpath('AppData', 'Roaming', 'Blender Foundation', 'Blender', blender_version,
                                    'extensions')

    @staticmethod
    def get_b3d_repo_index_file(blender_version: str) -> tuple[bool, Union[dict[str, Path], None, str]]:
        """

        :param version:
        :return:
            bool: True if success
            None or dict '{repo_name:index_file}'
        """
        d = Repos.get_b3d_ext_dir(blender_version)
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
