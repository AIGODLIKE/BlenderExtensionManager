from nicegui import ui
from view_model.blender_card import load_all, select_blender
from translation import _p


def draw():
    with ui.row().classes('w-full'):
        ui.space()
        with ui.button_group().props('rounded'):
            with ui.button(icon='add', on_click=lambda: select_blender(container)).classes('h-12'):
                ui.tooltip(_p('Add')).style('font-size: 100%')

            with ui.button(icon='refresh').classes('h-12'):
                ui.tooltip(_p('Verify All')).style('font-size: 100%')

    with ui.row().classes('w-full') as container:
        load_all(container)
