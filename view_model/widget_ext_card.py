from nicegui import ui, app
from typing import Union, Callable, Optional
from functools import partial
from pathlib import Path
import asyncio
import os

from model.schema import Schema, ExtensionsOptional
from translation import _p
from view_model.widget_ext_card_edit_dialog import CardEditDialog
from view_model.functions import remove_repo_index_by_id, get_b3d_ext_dir


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
    def __init__(self, data: dict, search_field: Optional[ui.input] = None):
        super().__init__()
        self.schema = Schema(data)
        self.data = data
        self.repo_name = ''
        self.expand = False
        self.addon_path = None  # Path to the __init__.py file of the addon
        self.search_field = search_field

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
            ui.label(_p('This action only remove blender register')).style('font-size: 80%')
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

    def on_dbclick_copy(self, text: str):
        if isinstance(text, str):
            ui.clipboard.write(text)
            ui.notify(_p('Copied') + ' ' + text)

    def on_tag_click(self, v):
        if self.search_field:
            if self.search_field.value == '':
                self.search_field.value = v.sender.text
            else:
                self.search_field.value += '+' + v.sender.text

    async def build_zip(self):
        from webview import SAVE_DIALOG
        from view_model.functions import build_addon_zip_file
        save_path = await  app.native.main_window.create_file_dialog(save_filename=f'{self.data.get("name")}.zip',
                                                                     dialog_type=SAVE_DIALOG,
                                                                     directory='/')
        if not save_path: return
        fp = Path(save_path)
        if fp.exists():
            try:
                fp.unlink()
            except:
                ui.notify(_p('File exists and cannot be deleted'), type='negative')
                return

        if self.addon_path:
            if fp.parent.resolve() == self.addon_path:
                ui.notify(_p('Cannot save inside source add-on folder'), type='warning',close_button='OK')
                return
            tg_dir = self.addon_path
            n = ui.notification(message=_p('Building Zip...'), spinner=True, type='ongoing', timeout=None)
            Schema.write_toml(directory=self.addon_path, data=self.data)
            res, msg = build_addon_zip_file(tg_dir, fp)
            n.spinner = False
            if res:
                n.message = _p('Done')
                n.type = 'positive'
                n.icon = 'done'
            else:
                n.message = _p('Failed') + f': {msg}'
                n.multi_line = True
                n.type = 'negative'
                n.icon = 'error'
            n.spinner = False
            if res:
                await asyncio.sleep(2)
                n.dismiss()

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
                    ui.chip(tag, color='primary', text_color='primary', on_click=self.on_tag_click) \
                        .props('outline')

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
                with ui.button(icon='archive', on_click=lambda: self.build_zip()).props('round flat') \
                        .bind_visibility_from(self, 'addon_path', lambda v:v):
                    ui.tooltip(_p('Build Zip')).style('font-size: 100%')

                ui.button(icon='close', on_click=lambda: self.remove_card()).props('round flat color="red"') \
                    .bind_visibility_from(self, 'addon_path', lambda v: not v)

    def draw_expand(self):
        with ui.card_section().classes('w-full').props('dense-toggle'):
            with ui.element('q-list').props('dense bordered'):
                # Required data
                with ui.element('q-item').classes('items-center').props('clickable') \
                        .on('dblclick', lambda: self.on_dbclick_copy(self.data.get('id'))):
                    ui.label('ID')
                    ui.space()
                    ui.label(self.data.get('id')).classes('font-semibold')
                with ui.element('q-item').classes('items-center').props('clickable') \
                        .on('dblclick', lambda: self.on_dbclick_copy(self.data.get('maintainer'))):
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
                                .on('dblclick', lambda: self.on_dbclick_copy(self.data.get(k))):
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
