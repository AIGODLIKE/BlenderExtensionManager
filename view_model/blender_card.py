from nicegui import ui, app
from pathlib import Path
from translation import _p
import subprocess
import asyncio
from model.blender import Blender


async def verify_blender(container):
    files = await app.native.main_window.create_file_dialog(allow_multiple=False)
    if not files: return
    f = files[0]
    if not f.endswith('blender.exe'):
        ui.notify('Invalid Blender', type='negative')
        return
    n = ui.notification(message="Verify Blender...", spinner=True, type="ongoing", timeout=None)
    await asyncio.sleep(1)
    b3d = Blender()
    b3d.path = f
    popen = subprocess.Popen([f, '-b', '--factory-startup'],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in iter(popen.stdout.readline, b''):
        s = line.decode('utf-8').strip()
        if b3d.init_from_str(s):
            n.message = _p(f'Blender verified:') + b3d.version
            n.spinner = False
            n.icon = 'done'
            n.type = 'positive'
            break
    popen.kill()
    if not b3d.is_valid:
        n.message = 'Invalid Blender'
        n.spinner = False
        n.icon = 'error'
        n.type = 'negative'

    with container:
        with ui.element('q-intersection').props('transition="scale"'):
            blender_card(b3d)
    b3d.update_db()
    await asyncio.sleep(1)


def draw_build_info(b3d):
    ui.label(f'Version: {b3d.version}')
    ui.label(f'Date: {b3d.date}')
    ui.label(f'Hash: {b3d.hash}')
    ui.label(f'Path: {b3d.path}')


def blender_card(b3d: Blender = None):
    with ui.card().classes('w-64 h-48'):
        with ui.dialog() as dialog, ui.card().classes('w-96 items-start'):
            with ui.row().classes('w-full items-center gap-0'):
                with ui.element('q-list'):
                    draw_build_info(b3d)

        with ui.column().classes('w-full items-start gap-0'):
            with ui.row().classes('w-full items-center px-0 gap-0'):
                ui.label(b3d.version).classes('text-lg')
                ui.space()
                ui.button(icon='info', on_click=lambda: dialog).props('dense rounded flat color="primary"')
                edit = ui.checkbox().props('checked-icon="edit" unchecked-icon="edit_off"')
                ui.button(icon='close').props('dense rounded flat color="red"')
            ui.space()
            path_input = ui.input(value=b3d.path).props(
                'dense flat color="primary" outlined autogrow').classes('w-full').bind_enabled_from(edit, 'value')
            with path_input.add_slot('append'):
                ui.button(icon='folder').props('dense flat color="primary"')


def draw_all_b3d_cards():
    with ui.row().classes('w-full'):
        ui.space()
        with ui.button_group().props('rounded'):
            with ui.button(icon='add', on_click=lambda: verify_blender(container)).classes('h-12'):
                ui.tooltip(_p('Add')).style('font-size: 100%')

            with ui.button(icon='refresh').classes('h-12'):
                ui.tooltip(_p('Verify All')).style('font-size: 100%')

    with ui.row().classes('w-full') as container:
        blenders = Blender.load_all_from_db()
        for b in blenders:
            blender_card(b)

# draw_all_b3d_cards()


# qfile = ui.element('q-file').props('filled label="Drop File Here"')
# qfile.on('update:modelValue', lambda e: print(f"File: '{e.args}'"))

# ui.run(native=True)
