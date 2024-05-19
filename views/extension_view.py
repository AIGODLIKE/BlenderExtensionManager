from nicegui import ui

from view_model.widget_ext_card import get_b3d_local_repos, parse_repo_index_file, ExtensionCard
from translation import _p


@ui.refreshable
def draw():
    repos, set_repos = ui.state(list(get_b3d_local_repos().keys()))
    repo, set_repo = ui.state('user_default')
    name_index = get_b3d_local_repos(version='4.2')
    index_file = name_index.get(repo, None)
    datas, set_datas = ui.state(parse_repo_index_file(index_file))
    selects = {repo: repo for repo in repos}
    cards = []

    def refresh_repos():
        repos = list(get_b3d_local_repos().keys())
        set_repos(repos)
        reports = '\n'.join(repos)
        ui.notify(f'{reports}')

    def toggle_expand():
        is_expand = False
        for i, c in enumerate(cards):
            if i == 0: is_expand = c.expand
            c.expand = (not is_expand)

    def reload():
        index_file = name_index.get(repo, None)
        datas = parse_repo_index_file(index_file)
        print(datas)
        set_datas(datas)
        ui.update()
        ui.notify('Refreshed')

    with ui.row().classes('w-full items-center'):
        with ui.select(selects, value=repo, on_change=lambda v: set_repo(v.value), label=_p('Repo')) \
                .props('outlined').style("min-width:200px; max-width: 300px") \
                .add_slot('append'):
            ui.icon('refresh').on('click', refresh_repos)
        ui.space()
        ui.button('Expand', on_click=toggle_expand)
        ui.button('Refresh', on_click=reload)
        ui.button('Save', on_click=lambda: ui.notify('Save'))

    for d in datas:
        with ui.column().classes('w-full px-0 p-0'):
            with ExtensionCard(d).classes('w-full shadow-2').tight() as card:
                card.draw()
                card.repo_name = repo
            cards.append(card)
