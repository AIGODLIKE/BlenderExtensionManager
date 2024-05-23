from nicegui import ui
from pathlib import Path
from translation import _p
def draw_build_info():
    ui.label('Version: 4.2.0 stable')
    ui.label('Date: 2024-5-20')
    ui.label('Hash: 8f9fa07cc16')
    ui.label('Branch: main')

def blender_card():
    with ui.card().classes('w-64 h-24'):
        with ui.dialog() as dialog, ui.card().classes('w-96 items-start'):
            with ui.row().classes('w-full items-center gap-0'):
                path_input = ui.input(value='/path/to/blender/exe').classes('w-full').props(
                    'dense flat color="primary" outlined')
                with path_input.add_slot('append'):
                    ui.button(icon='folder').props('dense flat color="primary"')
            with ui.element('q-list'):
                draw_build_info()


        with ui.column().classes('w-full items-start gap-0'):
            with ui.row().classes('w-full items-center px-0 gap-0'):
                ui.label('4.2.0 stable').classes('text-lg')
                ui.space()
                ui.button(icon='info', on_click=lambda: dialog).props('dense rounded flat color="primary"')
                ui.button(icon='folder').props('dense rounded flat color="primary"')
                ui.button(icon='close').props('dense rounded flat color="red"')
            ui.label('/path/to/blender/exe')



def draw_all_b3d_cards():
    with ui.row().classes('w-full'):
        ui.space()
        with ui.button_group().props('rounded'):
            with ui.button(icon='add', ).classes('h-12'):
                ui.tooltip(_p('Add')).style('font-size: 100%')

            with ui.button(icon='refresh').classes('h-12'):
                ui.tooltip(_p('Verify All')).style('font-size: 100%')

    with ui.row().classes('w-full'):
        for i in range(0, 5):
            blender_card()



draw_all_b3d_cards()
ui.run(native=True)
