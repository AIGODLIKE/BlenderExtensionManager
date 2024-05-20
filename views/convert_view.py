import shutil
from nicegui import ui, events, app
from pathlib import Path
import asyncio

from view_model.bl_info_card import draw_bl_info_card
from view_model.functions import write_repo_index_with_id
from translation import _p
from public_path import get_b3d_ext_dir
from model.schema import Schema


class State():
    filepath = ''


@ui.refreshable
def draw():
    async def refresh_bl_info():
        try:
            container.clear()
            with container:
                draw_bl_info_card(Path(State.filepath))
        except Exception as e:
            print(e)

    async def choose_file():
        files = await app.native.main_window.create_file_dialog(allow_multiple=False)
        if files:
            State.filepath = files[0]
            ui.notify(_p('Selected') + ': ' + State.filepath)

    async def copy2clipboard():
        ui.clipboard.write(State.filepath)
        ui.notify(_p('Copied') + ': ' + State.filepath)

    async def copy2repo(repo: str):
        fp = Path(State.filepath)
        card = dest_dir = None
        children = list(container.default_slot.children)
        if len(children) == 1:
            card = children[0]
            dest_dir = get_b3d_ext_dir(version='4.2').joinpath(repo, card.data.get('id'))
        if not card:
            ui.notify(_p('No Add-on Found'), type='negative')
            return
        if not dest_dir.exists():
            dest_dir.mkdir(parents=True)
        try:
            if dest_dir.exists():
                shutil.rmtree(dest_dir)
            if fp.name == '__init__.py':
                shutil.copytree(fp.parent, dest_dir, dirs_exist_ok=True)
            else:
                shutil.copy2(fp, dest_dir)
            Schema.write(directory=dest_dir, data=card.data)
            write_repo_index_with_id(repo, card.data)
        except Exception as e:
            ui.notify(_p(f'Install Failed') + f':{e}', multi_line=True, close_button='OK', type='negative')
            return

        ui.notify(_p('Install Success'), type='positive')

    with ui.row().classes('w-full items-center'):
        pick_file = ui.input(value='', placeholder=_p('Select a .py file'), on_change=refresh_bl_info) \
            .on('click', choose_file) \
            .props('readonly outlined') \
            .style('min-width:400px;max-width:800px').bind_value(State, 'filepath')

        with pick_file.add_slot('append'):
            ui.button(icon='content_copy', on_click=copy2clipboard) \
                .bind_visibility_from(pick_file, 'value', lambda v: v != '').props('flat color="primary"')
        with pick_file.add_slot('prepend'):
            ui.icon('folder').on('click', choose_file) \
                .props('flat color="primary"').bind_visibility_from(pick_file, 'value', lambda v: v == '')
        ui.space()

        with ui.button_group().props('rounded'):
            with ui.button(icon='refresh', on_click=refresh_bl_info): pass
            with ui.button(icon='install_desktop', on_click=lambda: copy2repo('user_default')) \
                    .classes('h-12') \
                    .props('color="primary"'):
                ui.tooltip(_p('Send to Repo')).style('font-size: 100%')
            with ui.button(icon='create_new_folder') \
                    .classes('h-12').props('color="primary"'):
                ui.tooltip(_p('Pack to .zip extension')).style('font-size: 100%')

    with ui.column().classes('w-full') as container:
        draw_bl_info_card(Path(State.filepath))
