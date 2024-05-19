from nicegui import ui
from typing import Callable
from public_path import get_b3d_local_repos
from view_model.ext_card import draw_all_cards
from translation import _p


@ui.refreshable
def draw():
    repos, set_repos = ui.state(list(get_b3d_local_repos()))
    repo, set_repo = ui.state('user_default')
    selects: dict = {repo: repo for repo in repos}

    def refresh_repos():
        new_repos = list(get_b3d_local_repos())
        set_repos(new_repos)
        set_repo('user_default')

        list_all_cards.clear()
        with list_all_cards:
            draw_all_cards(repo)

        reports = '\n'.join(new_repos)
        ui.notify(f'{_p("Refresh") + " " + reports}')

    with ui.row().classes('w-full items-center'):
        with ui.select(selects, value=repo, on_change=lambda v: set_repo(v.value), label=_p('Repo')) \
                .props('outlined').style("min-width:200px; max-width: 300px") \
                .add_slot('append'):
            ui.icon('refresh').on('click', refresh_repos)
        ui.space()
        ui.button('Save', on_click=lambda: ui.notify('Save'))

        with ui.column().classes('w-full px-0 p-0') as list_all_cards:
            draw_all_cards(repo)
