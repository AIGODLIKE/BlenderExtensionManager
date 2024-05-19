from nicegui import ui
from typing import Union, Callable
from functools import partial

from public_path import get_b3d_ext_dir
from model.schema import Schema, ExtensionsOptional
from translation import _p
from view_model.widget_ext_card_edit_dialog import CardEditDialog





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
        self.set_data(res)
        self.set_expand(self.expand)
        ui.update(self)
        ui.notify(self.data.get('name') + ' ' + _p(f'Edit Saved!'))

    def draw_header(self):

        with ui.row(wrap=False).classes('w-full items-center'):
            ui.label(self.data.get('name')).classes('font-semibold')
            ui.label(self.data.get('version')).classes('font-style: italic')

            ui.space()

            tags = self.data.get('tags', [])
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
