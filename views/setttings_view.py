from nicegui import app, ui
from translation import _p
from model.config import Config
from contextlib import contextmanager
from typing import Callable

dark = ui.dark_mode()
config = Config()
dark_mode = app.storage.general.get('dark_mode', 'white')


def setup_theme(dark_mode: str):
    if dark_mode == 'dark':
        dark.enable()
    elif dark_mode == 'white':
        dark.disable()
    else:
        dark.auto()


setup_theme(dark_mode)


def on_change_theme(v, tabs):
    setup_theme(v.value)
    value = 'white' if not dark.value else 'dark'
    tabs.props(f'active-bg-color="{value}"')


def on_change_lang(v):
    ui.notify(_p('Language set, save config and restart the program to take effect'))


def basic_card(text: str) -> ui.element:
    with ui.column().classes('w-full px-0 p-0 gap-1 items-center'):
        with ui.card().classes('w-96 gap-5 no-shadow').tight().props('bordered'):
            with ui.row().classes('w-full items-center px-2') as card:
                ui.label(_p(text))
                ui.space()
                return card


def draw(tabs: ui.element):
    with ui.row().classes('w-full'):
        ui.space()
        # ui.button(_p('Save'), icon='save', on_click=save_config).props('rounded no-caps').classes('h-12')

    with ui.column().classes('w-full px-0 p-0 gap-1 items-center'):
        with basic_card("Default Tab"):
            ui.select(options={
                'Blender': _p('Blender'),
                'Extensions': _p('Extensions'),
                'Settings': _p('Settings')
            }, ).bind_value(app.storage.general, 'default_tab')

        with basic_card("Theme"):
            ui.select(options={
                'white': _p('White'),
                'dark': _p('Dark'),
            }, on_change=lambda v: on_change_theme(v, tabs)).bind_value(app.storage.general, 'dark_mode')

        with basic_card("Language"):
            ui.select(options={
                'zh_CN': '中文',
                'en_US': 'English'
            }, on_change=on_change_lang).bind_value(app.storage.general, 'language')
