from nicegui import app, ui
from translation import _p
from translation import config as _t_config
from model.config import Config

dark = ui.dark_mode()
config = Config()
dark_mode = config.data.get('dark_mode', 'auto')


def init_theme(dark_mode: str):
    if dark_mode == 'dark':
        dark.enable()
    elif dark_mode == 'white':
        dark.disable()
    else:
        dark.auto()


init_theme(dark_mode)


def save_config():
    config._save()
    _t_config._load()
    ui.notify(_p('Config saved, restart the program to take effect'), type='positive')


def on_change_theme(v):
    theme_map = {
        False: 'white',
        True: 'dark',
        None: 'auto'
    }

    init_theme(v.value)
    config.data['dark_mode'] = theme_map[dark.value]


def on_change_lang(v):
    config.data['language'] = v.value
    ui.notify(_p('Language set, save config and restart the program to take effect'))


def on_change_tab(v):
    config.data['default_tab'] = v.value
    config._save()


def draw():
    with ui.row().classes('w-full'):
        ui.space()
        ui.button(_p('Save'), icon='save', on_click=save_config).props('rounded')

    with ui.column().classes('w-full px-0 p-0 gap-1 items-center'):
        with ui.card().classes('w-64 gap-5 no-shadow').tight().props('bordered'):
            with ui.row().classes('w-full items-center px-2'):
                ui.label(_p("Default Tab"))
                ui.space()
                ui.select(value=config.data['default_tab'], options=['Extensions', 'Convert', 'Settings'],
                          on_change=on_change_tab)

        with ui.card().classes('w-64 gap-5 no-shadow').tight().props('bordered'):
            with ui.row().classes('w-full items-center px-2'):
                ui.label(_p("Theme"))
                ui.space()
                ui.select(value=config.data['dark_mode'], options={
                    'white': _p('White'),
                    'dark': _p('Dark'),
                    'auto': _p('Auto')
                }, on_change=on_change_theme)

        with ui.card().classes('w-64 gap-5 no-shadow').tight().props('bordered'):
            with ui.row().classes('w-full items-center px-2'):
                ui.label(_p("Language"))
                ui.space()
                ui.select(value=config.data['language'], options={
                    'zh_CN': '中文',
                    'en_US': 'English'
                }, on_change=on_change_lang)
