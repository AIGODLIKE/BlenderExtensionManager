from nicegui import ui, app
from views import extension_view


def draw():
    with ui.header().classes(replace='row items-center pywebview-drag-region', ) as header:
        ui.button(icon='menu', on_click=lambda: left_drawer.toggle()).props('flat color=white')
        ui.button(on_click=app.shutdown, icon='close').props('flat color=white')

    with ui.left_drawer().classes('w-full px-0 p-0').props('width=100 breakpoint=500') as left_drawer:
        with ui.tabs().props(
                'switch-indicator vertical swipeable active-color="primary" indicator-color="primary"') as tabs:
            # ui.image(get_image('blender.png')).props('w-full h-1/2')
            with ui.tab('Extensions', icon='list').props('flat color=white'):
                # ui.badge('5+').props('color="red" floating')
                pass
            ui.tab('Settings', icon='settings').props('flat color=white')

    with ui.tab_panels(tabs, value='Extensions').classes('w-full h-full px-0 p-0').props(
            'transition-prev=jump-up transition-next=jump-up'):
        with ui.tab_panel('Extensions'):
            extension_view.draw()
        with ui.tab_panel('Settings'):
            pass
