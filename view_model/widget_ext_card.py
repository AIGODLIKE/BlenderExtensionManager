from nicegui import ui
from typing import Union, Callable
from functools import partial
from pathlib import Path

from public_path import get_b3d_ext_dir
from model.schema import Schema, ExtensionsOptional
from translation import _p
from view_model.widget_ext_card_edit_dialog import CardEditDialog
from view_model.functions import remove_repo_index_by_id


def open_file(repo_name: str, id: str, designation: Union[None, Path] = None):
    """open explorer or finder"""
    import sys, os
    if designation is not None:
        fp = designation
    else:
        fp = get_b3d_ext_dir().joinpath(repo_name, id)
    if not fp.exists():
        return
    if sys.platform == 'win32':
        os.startfile(fp)
    else:
        ui.notify(f'Platform not support yet', type='negative')


class ExtensionCard(ui.card):
    def __init__(self, data: dict):
        super().__init__()
        self.schema = Schema(data)
        self.data = data
        self.repo_name = ''
        self.expand = False
        self.addon_path = None  # Path to the __init__.py file of the addon

        with self:
            self.draw()

    async def open_edit_dialog(self):
        res: Union[None, dict] = await CardEditDialog(self.data)
        if not res: return
        self.data = res
        # print(self.data)
        ui.notify(self.data.get('name') + ' ' + _p(f'Edit Saved!'))
        self.update()
        self.clear()

        with self:
            self.draw()

    async def remove_card(self):
        # remove card from the container
        with ui.dialog() as dialog, ui.card().classes('items-center'):
            ui.label(_p('Are you sure to remove') + ' ' + self.data.get('name') + ' ?')
            with ui.row().classes('w-full'):
                ui.button('No', on_click=lambda: dialog.submit(False)).props('flat color="primary"')
                ui.button('Yes', on_click=lambda: dialog.submit(True)).props('color="red"')
        result = await dialog
        if result:
            res, msg = remove_repo_index_by_id(self.repo_name, self.data.get('id'))
            if res:
                ui.notify(_p('Removed') + ' ' + self.data.get('name'))
                self.clear()
                self.delete()
                ui.update()
            else:
                ui.notify(msg, type='negative')

    def draw(self):
        with ui.expansion().bind_value(self, 'expand') \
                .classes('w-full') \
                .props('dense expand-icon-toggle expand-separator switch-toggle-side') as expansion:
            with expansion.add_slot('header'):
                self.draw_header()
            self.draw_expand()

    def copy_text(self, text: str):
        if isinstance(text, str):
            ui.clipboard.write(text)
            ui.notify(_p('Copied') + ' ' + text)

    def draw_header(self):
        with ui.row(wrap=True).classes('w-full items-center gap-2'):
            is_valid, msg = Schema.is_valid(self.data)
            if not is_valid:
                with ui.icon('error').props('color="red"'):
                    ui.tooltip(msg).style('font-size: 100%')

            ui.label(self.data.get('name')).classes('font-semibold')
            ui.label(self.data.get('version')).classes('font-style: italic')

            ui.space()

            tags = self.data.get('tags', [])
            ui.label(_p(self.data.get('type'))).classes('font-medium')
            with ui.row().classes('gap-0'):
                for tag in tags:
                    ui.chip(tag, color='primary', text_color='primary').props('outline')

            with ui.button_group().props('flat'):
                with ui.button(icon='folder',
                               on_click=lambda: open_file(
                                   repo_name=self.repo_name,
                                   id=self.data.get('id'),
                                   designation=self.addon_path)
                               ).props('round flat'):
                    ui.tooltip(_p('Open Directory')).style('font-size: 100%')
                with ui.button(icon='edit', on_click=lambda: self.open_edit_dialog()).props('round flat'):
                    ui.tooltip(_p('Edit')).style('font-size: 100%')
                if not self.addon_path:  # only extension card
                    ui.button(icon='close', on_click=lambda: self.remove_card()).props('round flat color="red"')

    def draw_expand(self):
        with ui.card_section().classes('w-full').props('dense-toggle'):
            with ui.element('q-list').props('dense bordered'):
                # Required data
                with ui.element('q-item').classes('items-center').props('clickable') \
                        .on('dblclick', lambda: self.copy_text(self.data.get('id'))):
                    ui.label('ID')
                    ui.space()
                    ui.label(self.data.get('id')).classes('font-semibold')
                with ui.element('q-item').classes('items-center').props('clickable') \
                        .on('dblclick', lambda: self.copy_text(self.data.get('maintainer'))):
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
                        with ui.element('q-item').classes('w-full items-center').props('clickable') \
                                .on('dblclick', lambda: self.copy_text(self.data.get(k))):
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
