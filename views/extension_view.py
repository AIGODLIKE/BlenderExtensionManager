from nicegui import ui, events
from typing import Callable
from public_path import get_b3d_local_repos
from view_model.ext_card import draw_all_cards, save_all_cards
from translation import _p


@ui.refreshable
def draw():
    repos, set_repos = ui.state(list(get_b3d_local_repos()))
    repo, set_repo = ui.state('user_default')
    selects: dict = {repo: repo for repo in repos}

    def refresh_repos():
        list_all_cards.clear()

        new_repos = list(get_b3d_local_repos())
        set_repos(new_repos)
        set_repo('user_default')

        with list_all_cards:
            draw_all_cards(repo)

        reports = '\n'.join(new_repos)
        ui.notify(f'{_p("Reload") + " " + reports}')

    async def search(e: events.ValueChangeEventArguments) -> None:
        list_all_cards.clear()
        with list_all_cards:
            draw_all_cards(repo, e.value)

    with ui.row().classes('w-full items-center'):
        with ui.select(selects, value=repo, on_change=lambda v: set_repo(v.value), label=_p('Repo')) \
                .props('outlined').style("min-width:200px; max-width: 300px") \
                .add_slot('prepend'):
            ui.icon('settings').on('click', lambda: ui.notify('Settings'))

        search_field = ui.input(on_change=search, placeholder=_p('Search')) \
            .props('outlined rounded item-aligned input-class="ml-3" debounce="500"') \
            .classes('w-64 transition-all')
        with search_field.add_slot('prepend'):
            ui.icon('search')
        with search_field.add_slot('append'):
            ui.icon('close').props('clickable').on('click', lambda: search_field.set_value(''))

        ui.space()
        with ui.button_group().props('rounded'):
            with ui.button(icon='replay', on_click=refresh_repos).classes('h-12'):
                ui.tooltip(_p('Reload From Disk')).style('font-size: 100%')

            with ui.button(icon='save', on_click=lambda: save_all_cards(list_all_cards, repo)).classes('h-12'):
                ui.tooltip(_p('Save All')).style('font-size: 100%')

        with ui.column().classes('w-full px-0 p-0') as list_all_cards:
            draw_all_cards(repo)
