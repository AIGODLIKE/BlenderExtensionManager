from nicegui import ui, events
from model.schema import Schema, ExtensionsOptional
from translation import _p
from view_model.widget_tags_edit_dialog import TagsEditDialog

empty_validation = {
    _p('Required'): lambda v: v != '',
    _p('Length must be 3 or more'): lambda v: len(v) >= 3,
}
version_validation = {
    _p('Required'): lambda v: v != '',
    _p('Must be x.x.x'): lambda v: v.count('.') == 2 and all([i.isdigit() for i in v.split('.')]),
}


class CardEditDialog(ui.dialog):
    def __init__(self, data: dict):
        super().__init__()
        self.scheme = Schema(data)
        # self.keyboard = ui.keyboard(on_key=lambda e: self.handle_keyboard(e))

        with self.props('position="right"'), ui.card().classes('w-full items-center').props('rounded'):
            self.draw()

    def draw(self):
        ui.input(label=_p('name'), validation=empty_validation, ) \
            .bind_value(self.scheme, 'name') \
            .style('min-width:400px; max-width: 600px').props('hide-bottom-space')

        # ui.input(label=_p('id')).bind_value(self.scheme, 'id').style('min-width:400px; max-width: 600px')
        ui.select({'add-on': _p('add-on'), 'theme': _p('theme')}, value='add-on', label=_p('type')).bind_value(
            self.scheme, 'type').classes('w-full')

        for k, v in self.scheme.__annotations__.items():
            if k in ['name', 'id', 'type', 'schema_version']:
                continue
            elif k in ['tags','license'] and isinstance(getattr(self.scheme, k), list):
                tag_list = getattr(self.scheme, k)
                with ui.row(wrap=False).classes('w-full gap-0 px-1 items-center') as tag_row:
                    self.draw_tags(k, tag_list, tag_row)

                ui.separator()
            elif k in ['version', 'blender_version_min', 'blender_version_max']:
                ui.input(label=_p(k), validation=version_validation).bind_value(self.scheme, k).style(
                    'min-width:400px; max-width: 600px').props('mask="#.#.#" hint="x.x.x" hide-bottom-space')
            elif k in ['tagline', 'maintainer', 'website']:
                ui.input(value=getattr(self.scheme, k, ''), label=_p(k), validation=empty_validation) \
                    .bind_value(self.scheme, k).style('min-width:400px; max-width: 600px').props(
                    'hide-bottom-space')
            else:
                ui.input(label=_p(k)).bind_value(self.scheme, k).style('min-width:400px; max-width: 600px')
        ui.update()
        with ui.element('q-list').props('bordered'):
            for k in ExtensionsOptional.__annotations__.keys():
                if hasattr(self.scheme, k):
                    if k in ['permissions', 'platforms']: continue
                    ui.input(label=_p(k)).bind_value(self.scheme, k).style('min-width:400px; max-width: 600px')

        with ui.row():
            ui.button(_p('Cancel'), on_click=lambda: self.submit(None)).props('flat')
            ui.button(_p('Save'), on_click=lambda: self.handle_ok())

    async def open_tags_dialog(self, attr: str, tag_row: ui.row):
        tags = getattr(self.scheme, attr)
        new_tags = await TagsEditDialog(tags)
        if new_tags is None:
            return
        elif len(new_tags) == 0:
            ui.notify(_p('At least one tag'),type= 'warning')
            return
        if new_tags == tags:
            ui.notify(_p('No change'),type='warning')
            return
        setattr(self.scheme, attr, new_tags)
        tag_row.clear()
        with tag_row:
            self.draw_tags(attr, new_tags, tag_row)

        ui.notify(_p('Tags updated'))

    def draw_tags(self, k: str, tag_list: list, tag_row: ui.row):
        ui.button(_p(k), on_click=lambda a=k: self.open_tags_dialog(a, tag_row)) \
            .classes('w-[20%]') \
            .props('flat dense icon-right="edit"')

        for tag in tag_list:
            ui.chip(tag, color='primary', text_color='primary').props('outline')

    def handle_ok(self):
        data = self.scheme.to_dict()
        submit = True
        for k, v in data.items():
            if isinstance(v, list):
                if len(v) == 0:
                    ui.notify(f'{_p(k)} {_p("is empty")}', type='negative')
                    submit = False
            elif isinstance(v, str):
                if v == '':
                    ui.notify(f'{_p(k)} {_p("is empty")}', type='negative')
                    submit = False
        if submit:
            self.submit(self.scheme.to_dict())

    def handle_keyboard(self, e: events.KeyEventArguments):
        if e.key == 'Enter':
            self.handle_ok()
        elif e.key == 'Escape':
            self.submit(None)
