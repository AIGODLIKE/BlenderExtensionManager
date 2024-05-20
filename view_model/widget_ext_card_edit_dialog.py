from nicegui import ui, events
from model.schema import Schema, ExtensionsOptional
from translation import _p

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
            ui.input(label=_p('name'), validation=empty_validation, ) \
                .bind_value(self.scheme, 'name') \
                .style('min-width:400px; max-width: 600px').props('hide-bottom-space')

            # ui.input(label=_p('id')).bind_value(self.scheme, 'id').style('min-width:400px; max-width: 600px')
            ui.select({'add-on': _p('add-on'), 'theme': _p('theme')}, value='add-on', label=_p('type')).bind_value(
                self.scheme, 'type').classes('w-full')

            for k, v in self.scheme.__annotations__.items():
                if k in ['name', 'id', 'tags', 'type', 'schema_version']:
                    continue
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
