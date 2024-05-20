from pathlib import Path
from translation import _p


class RepoIndexFile():
    def __init__(self, fp: Path):
        self.fp = fp
        self.repo_name = self.fp.parent.parent.name
        self.backup_dir = self.fp.parent.parent.joinpath('.blender_ext_backup')
        self.data = self.parse()

    def parse(self, version: str = 'v1'):
        import json
        fp = self.fp
        with open(fp, mode='r', encoding='utf-8') as f:
            json_data = json.load(f)
            v = json_data.get('version')
            if v != version: return None
            d = json_data.get('data')
            return d

    def reload(self):
        self.data = self.parse()

    def backup(self) -> tuple[bool, str]:
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
        data_list: list = self.data.get('data')
        for i, d in enumerate(data_list):
            if d.get('id') == id:
                data_list.pop(i)
                break
        return self._write_all(data_list)
