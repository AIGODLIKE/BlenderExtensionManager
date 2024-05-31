from nicegui import ui, app
from pathlib import Path
from translation import _p
import subprocess
import asyncio
import os
from typing import Union, Optional
from model.blender import Blender
from public_path import get_icon_path
from view_model.global_worker import Worker


def open_file(file: Path):
    if not file.exists():
        return
    if os.name == 'nt':
        os.startfile(file.parent)


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
    b3d = Blender()
    b3d.path = f
    b3d = await verify_blender(b3d)
    if b3d:
        with container:
            with ui.element('q-intersection').props('transition="scale"'):
                BlenderCard(b3d, container)


async def verify_blender(b3d: Blender, set_active=True) -> Union[Blender, bool]:
    n = ui.notification(message=_p("Verify Blender..."), spinner=True, type="ongoing", timeout=3)

    async def _error_n():
        n.message = _p('Invalid Blender')
        n.spinner = False
        n.icon = 'error'
        n.type = 'negative'
        n.close_button = _p('OK')

    await asyncio.sleep(0.5)
    if not Path(b3d.path).exists():
        await _error_n()
        return False
    popen = subprocess.Popen([b3d.path, '-b', '--factory-startup'],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    try:
        stdout, stderr = popen.communicate(timeout=3)
        for line in iter(stdout.splitlines()):
            s = line.decode('utf-8').strip()
            if b3d.init_from_str(s):
                n.message = _p(f'Verified Success:') + f" {b3d.version}-{b3d.hash}"
                n.spinner = False
                n.icon = 'done'
                n.type = 'positive'
                break
    except:
        b3d.is_valid = False
    finally:
        popen.kill()

    b3d.save_to_db()

    if b3d.is_valid is False:
        await _error_n()
        return False

    if set_active:
        b3d.is_active = True
        app.storage.general['blender_path'] = b3d.path
        app.storage.general['blender_version'] = b3d.big_version

    return b3d


class BlenderCard(ui.card):
    def __init__(self, b3d: Blender, container: ui.element):
        super().__init__()
        self.blender = b3d
        self.container = container

        with self.classes('w-64 h-48 no-shadow').props('bordered'):
            with ui.column().classes('w-full items-start gap-1'):
                ui.image(get_icon_path('blender.png')).classes('h-1/3') \
                    .style('filter: grayscale(100%)').bind_visibility_from(self.blender, 'is_active', lambda v: not v)
                ui.image(get_icon_path('blender.png')).classes('h-1/3').bind_visibility_from(self.blender, 'is_active')

                with ui.column().classes('w-full items-start gap-1') as self.active_draw:
                    self.draw_active()
    @ui.refreshable
    def draw_active(self):
        b3d = self.blender
        with ui.row().classes('w-full items-center px-0 gap-1'):
            ui.label(b3d.version).classes('text-xl')

            ui.space()
            with ui.button(icon='info', on_click=lambda: open_file(Path(b3d.path))) \
                    .props('dense flat color="primary rounded"'):
                with ui.tooltip().classes(f'text-lg bg-primary shadow-2'):
                    with ui.element('q-list'):
                        ui.label(f'Version: {b3d.version}')
                        ui.label(f'Date: {b3d.date}')
                        ui.label(f'Hash: {b3d.hash}')
                        ui.label(f'Path: {b3d.path}')
            ui.button(icon='close', on_click=self.remove_blender).props(
                'dense rounded flat color="red"')

        ui.button(_p('Invalid')).classes('text-red-5 text-lg') \
            .bind_visibility_from(self.blender, 'is_valid', lambda v: not v) \
            .props('no-caps flat dense')
        with ui.row().bind_visibility_from(self.blender, 'is_valid'):
            ui.button(_p('Activated'), on_click=self.set_active).classes(
                'text-lg text-green-6').props(
                'no-caps flat dense') \
                .bind_visibility_from(self.blender, 'is_active')
            ui.button(_p('Active'), on_click=self.set_active).classes('text-lg text-grey-6').props(
                'no-caps flat dense') \
                .bind_visibility_from(self.blender, 'is_active', lambda v: not v)

    async def set_active(self):
        for c in self.container.default_slot.children:
            if c == self:
                self.blender.is_active = True
            elif isinstance(c, BlenderCard):
                c.blender.is_active = False
                c.blender.save_to_db()

        res = await verify_blender(self.blender, set_active=False)
        if res:
            app.storage.general['blender_path'] = res.path
            app.storage.general['blender_version'] = res.big_version
        self.blender = res
        self.draw_active.refresh()

    def remove_blender(self):
        self.blender.remove_from_db()
        ui.notify(_p('Removed'))
        self.delete()


def load_all(container: ui.element):
    blenders = Blender.load_all_from_db()
    for b in blenders:
        if b.is_active:
            app.storage.general['blender_path'] = b.path
            app.storage.general['blender_version'] = b.big_version

        BlenderCard(b, container)

# qfile = ui.element('q-file').props('filled label="Drop File Here"')
# qfile.on('update:modelValue', lambda e: print(f"File: '{e.args}'"))

# ui.run(native=True)
