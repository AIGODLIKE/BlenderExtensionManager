from nicegui import ui, app
from views import extension_view, convert_view, setttings_view
from views.setttings_view import config
from translation import _p


def draw():
    bg_color = config.data.get('dark_mode')
    default_tab = config.data['default_tab']

    with ui.left_drawer().classes('px-0 p-2 bg-primary').props('width=100 breakpoint=400') as left_drawer:
        with ui.column().classes('w-full h-full items-center'):
            with ui.tabs().classes('w-full text-white') \
                    .props(
                f'vertical swipeable active-bg-color="{bg_color}" active-color="primary" indicator-color="transparent"') \
                    .style('margin-top:150px') as tabs:
                ui.tab('Extensions', label=_p('Extensions'), icon='extension').props('flat color=white no-caps')
                ui.tab('Convert', label=_p('Convert'), icon='change_circle').props('flat color=white no-caps')
                ui.tab('Settings', label=_p('Settings'), icon='settings').props('flat color=white no-caps')
            ui.button(icon='help', on_click=lambda: ui.notify('TODO')).props('flat color="white" dense rounded')

    with ui.element('q-toolbar').classes('items-center pywebview-drag-region h-12'):
        with ui.row().classes('w-full items-center px-0 p-0'):
            ui.button(icon='menu_open', on_click=lambda: left_drawer.toggle()).props('flat color="primary" dense')
            ui.space()
            ui.button(on_click=app.shutdown, icon='close').props('flat color="red" dense')

    with ui.tab_panels(tabs, value=default_tab).classes('w-full h-full px-0 p-0').props(
            'transition-prev=jump-up transition-next=jump-down'):
        with ui.tab_panel('Extensions'):
            extension_view.draw()
        with ui.tab_panel('Convert'):
            convert_view.draw()
        with ui.tab_panel('Settings'):
            setttings_view.draw(tabs)

    with ui.page_sticky(position='bottom-right', y_offset=10, x_offset=10):
        ui.label('Blender Extension Manager').classes('text-lg text-grey-5').style('font-family: "Comic Sans MS"')