from nicegui import ui

from view_model.widget_ext_card import get_b3d_local_repos, parse_repo_index_file, ExtensionCard
from translation import _p


def draw_all_cards(repo: str):
    name_index = get_b3d_local_repos(version='4.2')
    index_file = name_index.get(repo, None)
    datas = parse_repo_index_file(index_file)
    for d in datas:
        with ExtensionCard(d).classes('w-full shadow-1').tight() as card:
            card.repo_name = repo


@ui.refreshable
def draw():
    repos, set_repos = ui.state(list(get_b3d_local_repos().keys()))
    repo, set_repo = ui.state('user_default')
    selects = {repo: repo for repo in repos}

    def refresh_repos():
        new_repos = list(get_b3d_local_repos().keys())
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

    # cards.append(card)
