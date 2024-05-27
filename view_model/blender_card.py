from nicegui import ui, app
from pathlib import Path
from translation import _p
import subprocess
import asyncio
import re
from typing import Union
from model.blender import Blender
from public_path import get_icon_path


async def select_blender(container: ui.row):
    files = await app.native.main_window.create_file_dialog(allow_multiple=False)
    if not files: return
    f = files[0]
    if not f.endswith('blender.exe'):
        ui.notify(_p('Invalid Blender'), type='negative')
        return
    if Blender.is_path_in_db(f):
        ui.notify(_p('Already added this blender'), type='warning')
        return

    b3d = await verify_blender(f, container)
    if b3d:
        with container:
            with ui.element('q-intersection').props('transition="scale"'):
                BlenderCard(b3d, container)


async def verify_blender(fp: str, container: ui.row) -> Union[Blender, bool]:
    n = ui.notification(message=_p("Verify Blender..."), spinner=True, type="ongoing", timeout=None)
    await asyncio.sleep(0.5)
    b3d = Blender()
    b3d.path = fp
    popen = subprocess.Popen([fp, '-b', '--factory-startup'],
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
        n.message = _p('Invalid Blender')
        n.spinner = False
        n.icon = 'error'
        n.type = 'negative'
        return False

    b3d.save_to_db()
    await asyncio.sleep(1)
    n.dismiss()
    return b3d


class BlenderCard(ui.card):
    def __init__(self, b3d: Blender, container: ui.row):
        super().__init__()
        self.blender = b3d
        self.container = container
        self.classes('w-64 h-48 no-shadow').props('bordered')

        with ui.dialog() as dialog, ui.card().classes('w-96 items-start'):
            with ui.row().classes('w-full items-center gap-0'):
                path_input = ui.input(value=b3d.path).classes('w-full').props(
                    'dense flat color="primary" outlined autogrow')
                with path_input.add_slot('append'):
                    ui.button(icon='folder').props('dense flat color="primary"')

        with self:
            with ui.column().classes('w-full items-start gap-1'):
                with ui.image(get_icon_path('blender.png')).classes('h-1/3'):
                    pass

                with ui.row().classes('w-full items-center px-0 gap-1'):
                    with ui.icon('info', size='sm').props('dense flat color="primary"'):
                        with ui.tooltip().classes('text-lg'):
                            with ui.element('q-list'):
                                ui.label(f'Version: {b3d.version}')
                                ui.label(f'Date: {b3d.date}')
                                ui.label(f'Hash: {b3d.hash}')
                    ui.label(b3d.version).classes('text-xl')

                    ui.space()
                    ui.button(icon='edit', on_click=lambda: dialog).props('dense rounded flat color="primary"')
                    ui.button(icon='close', on_click=self.remove_blender).props(
                        'dense rounded flat color="red"')
                if self.blender.is_active:
                    # border color green width 2px
                    self.style('border-color:green;border-width:1.5px')
                ui.button(_p('Active'), on_click=lambda: ui.notify(_p('Already Active'))).classes(
                    'text-lg text-green-6').props(
                    'no-caps flat dense') \
                    .bind_visibility_from(self.blender, 'is_active')
                ui.button(_p('Active'), on_click=self.set_active).classes('text-lg text-grey-6').props(
                    'no-caps flat dense') \
                    .bind_visibility_from(self.blender, 'is_active', lambda v: not v)

    async def set_active(self):
        for c in self.container.default_slot.children:
            if c == self:
                b3d = await verify_blender(self.blender.path, self.container)
                if b3d:
                    c.blender = b3d
                    c.blender.is_active = True
                else:
                    c.blender.is_valid = False
                c.blender.save_to_db()
            elif isinstance(c, BlenderCard):
                c.blender.is_active = False
                c.blender.save_to_db()

        self.container.clear()
        with self.container:
            load_all(self.container)

    def remove_blender(self):
        self.blender.remove_from_db()
        ui.notify(_p('Removed'))
        self.container.clear()
        with self.container:
            load_all(self.container)


def load_all(container: ui.row):
    blenders = Blender.load_all_from_db()
    for b in blenders:
        BlenderCard(b, container)

# qfile = ui.element('q-file').props('filled label="Drop File Here"')
# qfile.on('update:modelValue', lambda e: print(f"File: '{e.args}'"))

# ui.run(native=True)
