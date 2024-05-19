from typing import Union
from nicegui import ui
from pathlib import Path
from translation import _p
from model.bl_info import Bl_info
from view_model.widget_ext_card import ExtensionCard
from view_model.ext_card import backup_repo_index, get_b3d_ext_dir


def write_repo_index_with_id(repo_name: str, data: dict, version: str = '4.2') -> tuple[bool, str]:
    # backup dir
    res, msg = backup_repo_index(repo_name)
    if not res: return (res, msg)

    import json
    fp = get_b3d_ext_dir(version).joinpath(repo_name, '.blender_ext', 'index.json')
    with open(fp, 'r', encoding='utf-8') as f:
        ori_data = json.load(f)

    data_list: list = ori_data.get('data')
    data_list.append(data)
    ori_data['data'] = data_list

    try:
        with open(fp, 'w', encoding='utf-8') as f:
            json.dump(ori_data, f, ensure_ascii=False, indent=4)
    except:
        return (False, f'write failed: {str(fp)}')

    return (True, f'write success: {str(fp)}')


def draw_bl_info_card(path: Path):
    if not path.is_file(): return

    bl_info = Bl_info()
    res, data = bl_info.setup(path)
    if not res:
        ui.notify(f'{_p("Error")}: {path}', type='negative')
        return
    schema_data = bl_info.to_schema_data()
    card = ExtensionCard(schema_data).classes('w-full').props('bordered')
    card.expand = True
