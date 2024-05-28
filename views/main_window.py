from nicegui import ui, app
from views import extension_view, convert_view, setttings_view, blender_view
from public_path import get_svg_str
from translation import _p


def draw():
    bg_color = app.storage.general.get('dark_mode','white')
    default_tab = app.storage.general.get('default_tab','Blender')
    version = app.storage.general.get("version")

    with ui.left_drawer().classes('px-0 p-2 bg-primary').props('width=100 breakpoint=400') as left_drawer:
        with ui.column().classes('w-full h-full items-center'):
            with ui.tabs().classes('w-full text-white') \
                    .props(
                f'vertical swipeable active-bg-color="{bg_color}" active-color="primary" indicator-color="transparent"') \
                    .style('margin-top:150px') as tabs:
                with ui.tab('Blender', label='').props('flat color=white no-caps'):
                    ui.html(get_svg_str('blender.svg')).classes('w-full')
                    ui.label(_p('Blender'))
                ui.tab('Extensions', label=_p('Extensions'), icon='extension').props('flat color=white no-caps')
                ui.tab('Settings', label=_p('Settings'), icon='settings').props('flat color=white no-caps')
            ui.button(icon='help', on_click=lambda: ui.notify('TODO')).props('flat color="white" dense rounded')
            ui.label('v'+version).classes('text-xs text-white')

    with ui.element('q-toolbar').classes('items-center pywebview-drag-region h-12'):
        with ui.row().classes('w-full items-center px-0 p-0'):
            ui.button(icon='menu_open', on_click=lambda: left_drawer.toggle()).props('flat color="primary" dense')
            with ui.tabs().classes('text-grey-6 ').props(
                    'active-color="primary" no-caps dense inline-label indicator-color="primary" narrow-indicator') \
                    .bind_visibility_from(tabs, 'value', lambda v: v == 'Extensions') as ext_tabs:
                ui.tab('Manage', icon='extension', label=_p('Manage Repo Extensions'))
                ui.tab('Convert', icon='change_circle', label=_p('Convert Addon to Extension'))
            ui.space()
            ui.button(on_click=app.shutdown, icon='close').props('flat color="red" dense')

    with ui.tab_panels(tabs, value=default_tab).classes('w-full h-full px-0 p-0').props(
            'transition-prev=jump-up transition-next=jump-down'):
        with ui.tab_panel('Blender').classes('w-full h-full px-0 p-2'):
            blender_view.draw()
        with ui.tab_panel('Extensions').classes('w-full h-full px-0 p-0'):
            with ui.tab_panels(ext_tabs, value='Manage').classes('w-full h-full px-0 p-0'):
                with ui.tab_panel('Manage').classes('w-full h-full px-2 p-2'):
                    extension_view.draw()
                with ui.tab_panel('Convert').classes('w-full h-full px-2 p-2'):
                    convert_view.draw()
        with ui.tab_panel('Settings'):
            setttings_view.draw(tabs)

    with ui.page_sticky(position='bottom-right', y_offset=10, x_offset=10):
        ui.label('Blender Extension Manager').classes('text-lg text-grey-5').style('font-family: "Comic Sans MS"')
