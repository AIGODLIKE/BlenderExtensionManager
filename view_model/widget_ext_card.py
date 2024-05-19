from nicegui import ui
from pathlib import Path
from typing import Union, Callable
from functools import partial

from public_path import get_b3d_local_repos, get_b3d_ext_dir
from model.schema import Schema, ExtensionsOptional
from translation import _p


def parse_repo_index_file(fp: Path, version: str = 'v1') -> Union[list[dict], None]:
    import json
    with open(fp, mode='r', encoding='utf-8') as f:
        json_data = json.load(f)
        v = json_data.get('version')
        if v != version: return None
        d = json_data.get('data')
        return d


def open_file(repo_name: str, id: str):
    import sys, os
    fp = get_b3d_ext_dir().joinpath(repo_name, id)
    if sys.platform == 'win32':
        os.startfile(fp)
    else:
        ui.notify(f'Platform not support yet', type='negative')


def write_json(repo_name, ori_id: str, data: dict):
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


class ExtensionCard(ui.card):
    def __init__(self, data: dict):
        super().__init__()
        self.schema = Schema(data)
        self.data, self.set_data = ui.state(data)
        self.repo_name = ''
        self.expand, self.set_expand = ui.state(False)

        with self:
            with ui.expansion().bind_value(self, 'expand') \
                    .classes('w-full') \
                    .props('dense expand-icon-toggle expand-separator switch-toggle-side') as expansion:
                with expansion.add_slot('header'):
                    self.draw_header()
                self.draw_expand()

    async def open_edit_dialog(self):
        res: Union[None, dict] = await CardEditDialog(self.data)
        if not res: return
        # write_json(self.repo_name, self.data.get('id'), res)
        self.set_data(res)
        self.set_expand(self.expand)
        ui.update(self)
        ui.notify(self.data.get('name') + ' ' + _p(f'Edit Saved!'))

    def draw_header(self):

        with ui.row(wrap=False).classes('w-full items-center'):
            ui.label(self.data.get('name')).classes('font-semibold')
            ui.label(self.data.get('version')).classes('font-style: italic')

            ui.space()

            tags = self.data.get('tags',[])
            ui.label(_p(self.data.get('type'))).classes('font-medium')
            with ui.row().classes('gap-0'):
                for tag in tags:
                    ui.chip(tag, color='primary', text_color='primary').props('outline')

            with ui.button_group().props('flat bordered'):
                with ui.button(icon='folder',
                               on_click=lambda: open_file(repo_name=self.repo_name, id=self.data.get('id'))).props(
                    'round flat'):
                    ui.tooltip(_p('Open Directory')).style('font-size: 100%')
                with ui.button(icon='edit', on_click=self.open_edit_dialog).props('round flat'):
                    ui.tooltip(_p('Edit')).style('font-size: 100%')

    def draw_expand(self):
        with ui.card_section().classes('w-full').props('dense-toggle'):
            with ui.element('q-list').props('dense bordered'):
                # Required data
                with ui.element('q-item').classes('items-center').props('clickable'):
                    ui.label('ID')
                    ui.space()
                    ui.label(self.data.get('id')).classes('font-semibold')
                with ui.element('q-item').classes('items-center').props('clickable'):
                    ui.label(_p('maintainer').title())
                    ui.space()
                    ui.label(self.data.get('maintainer'))
                # normal data
                for k, v in self.data.items():
                    if k in ['name', 'id', 'version', 'tags', 'schema_version', 'type', 'website',
                             'maintainer']:
                        continue
                    elif k in ExtensionsOptional.__annotations__.keys():
                        continue
                    else:
                        with ui.element('q-item').classes('w-full items-center').props('clickable'):
                            ui.label(_p(k))
                            ui.space()
                            ui.label(v)
                # website
                with ui.element('q-item').classes('w-full items-center'):
                    ui.label(_p('website'))
                    ui.space()
                    ui.button(_p('Open Website'), on_click=lambda: ui.open(self.data.get('website'), True))
                # Optional data
                with ui.expansion().classes('w-full').props('dense switch-toggle-side') as exp:
                    with exp.add_slot('header'):
                        with ui.row().classes('w-full items-center'):
                            ui.label(_p('Optional'))
                    with ui.element('q-list').classes('w-full').props('dense bordered'):
                        for k, v in self.data.items():
                            if k not in ExtensionsOptional.__annotations__.keys(): continue
                            with ui.element('q-item').classes('w-full items-center').props('clickable'):
                                ui.label(_p(k))
                                ui.space()
                                if isinstance(v, list):
                                    ui.label(', '.join(_p(i) for i in v))
                                else:
                                    ui.label(v)


class CardEditDialog(ui.dialog):
    def __init__(self, data: dict):
        super().__init__()
        self.scheme = Schema(data)
        with self.props('position="right"'), ui.card().classes('w-full items-center').props('rounded'):
            with ui.element('q-list').props('bordered'):
                ui.input(label=_p('name')).bind_value(self.scheme, 'name').style('min-width:400px; max-width: 600px')
                # ui.input(label=_p('id')).bind_value(self.scheme, 'id').style('min-width:400px; max-width: 600px')
                ui.select({'add-on': _p('add-on'), 'theme': _p('theme')}, value='add-on', label=_p('type')).bind_value(
                    self.scheme, 'type')

                for k, v in self.scheme.__annotations__.items():
                    if k in ['name', 'id', 'tags', 'type', 'schema_version']:
                        continue
                    else:
                        ui.input(label=_p(k)).bind_value(self.scheme, k).style('min-width:400px; max-width: 600px')

            with ui.row():
                ui.button(_p('Cancel'), on_click=lambda: self.submit(None)).props('flat')
                ui.button(_p('Save'), on_click=lambda: self.submit(self.scheme.to_dict()))
