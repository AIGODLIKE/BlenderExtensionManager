from typing import Union
from nicegui import ui
from pathlib import Path
from translation import _p
from model.baddoninfo import BAddonInfo
from view_model.widget_ext_card import ExtensionCard


def draw_bl_info_card(path: Path):
    if not path.is_file(): return

    bl_info = BAddonInfo()
    res, data = bl_info.setup(path)
    if not res:
        ui.notify(f'{_p("Error")}: {path}', type='negative')
        return
    schema_data = bl_info.to_schema_data()
    card = ExtensionCard(schema_data).classes('w-full').props('bordered')
    card.expand = True
    card.addon_path = path.parent
