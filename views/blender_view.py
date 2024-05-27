from nicegui import ui
from view_model.blender_card import load_all, select_blender, verify_blender, BlenderCard
from translation import _p


async def verify_all(container: ui.row):
    for c in container.default_slot.children:
        if not isinstance(c, BlenderCard): continue
        await verify_blender(c.blender, set_active=False)


def draw():
    with ui.row().classes('w-full'):
        ui.space()
        with ui.button_group().props('rounded'):
            with ui.button(icon='add', on_click=lambda: select_blender(container)).classes('h-12'):
                ui.tooltip(_p('Add')).style('font-size: 100%')

            with ui.button(icon='refresh', on_click=lambda: verify_all(container)).classes('h-12'):
                ui.tooltip(_p('Verify All')).style('font-size: 100%')

    with ui.row().classes('w-full') as container:
        load_all(container)
