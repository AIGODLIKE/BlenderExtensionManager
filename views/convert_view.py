import shutil
from nicegui import ui, events, app
from pathlib import Path
from view_model.bl_info_card import draw_bl_info_card
from view_model.functions import write_repo_index_with_id
from translation import _p
from public_path import get_b3d_ext_dir
from model.schema import Schema


@ui.refreshable
def draw():
    file, set_file = ui.state('')

    async def choose_file():
        files = await app.native.main_window.create_file_dialog(allow_multiple=False)
        if files:
            pick_file.value = files[0]
            set_file(files[0])
            ui.notify(_p('Selected') + ': ' + pick_file.value)

    async def refresh_bl_info():
        container.clear()
        with container:
            draw_bl_info_card(Path(file))

    async def copy2repo(repo: str):
        fp = Path(pick_file.value)
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
                print(fp.parent)
                print(dest_dir)
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
        pick_file = ui.input(value=file, placeholder=_p('Select a .py file'), on_change=refresh_bl_info).props(
            'readonly outlined').style('min-width:400px')
        with pick_file.add_slot('append'):
            with ui.button(icon='folder', on_click=choose_file).props('flat color="primary"'):
                ui.tooltip(_p('Choose File')).style('font-size: 100%')
        with pick_file:
            ui.tooltip(f"{pick_file.value}").style('font-size: 100%').bind_visibility_from(pick_file, 'value',
                                                                                           lambda v: v != '')
        ui.space()
        with ui.button('', icon='install_desktop', on_click=lambda: copy2repo('user_default')).props('color="primary"'):
            ui.tooltip(_p('Send to Repo')).style('font-size: 100%')

    with ui.column().classes('w-full') as container:
        draw_bl_info_card(Path(pick_file.value))
