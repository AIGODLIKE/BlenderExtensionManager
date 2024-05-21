from nicegui import ui, app
from views import extension_view, convert_view, setttings_view
from views.setttings_view import config
from translation import _p

def draw():
    with ui.header().classes(replace='row items-center pywebview-drag-region h-12') as header:
        with ui.row().classes('w-full items-center px-2'):
            ui.button(icon='menu', on_click=lambda: left_drawer.toggle()).props('flat color=white')
            ui.label('Blender Extension Manager').classes('text-lg').style('font-family: "Comic Sans MS"')
            ui.space()
            ui.button(on_click=app.shutdown, icon='close').props('flat color=white')


    with ui.left_drawer().classes('px-0 p-0').props('width=100 breakpoint=500') as left_drawer:
        with ui.tabs().classes('w-full text-grey-6').props(
                'switch-indicator vertical swipeable active-color="primary" indicator-color="primary"') as tabs:
            with ui.tab('Extensions',label=_p('Extensions'), icon='list').props('flat color=white'):
                # ui.badge('5+').props('color="red" floating')
                pass
            ui.tab('Convert',label=_p('Convert'), icon='change_circle').props('flat color=white')
            ui.tab('Settings',label=_p('Settings'), icon='settings').props('flat color=white')
    with ui.tab_panels(tabs, value=config.data['default_tab']).classes('w-full h-full px-0 p-0').props(
            'transition-prev=jump-up transition-next=jump-up'):
        with ui.tab_panel('Extensions'):
            extension_view.draw()
        with ui.tab_panel('Convert'):
            convert_view.draw()
        with ui.tab_panel('Settings'):
            setttings_view.draw()

    with ui.page_sticky(position='bottom-right',y_offset=10,x_offset=10):
        pass
