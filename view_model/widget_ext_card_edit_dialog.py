from nicegui import ui, events
from model.schema import Schema, ExtensionsOptional
from translation import _p


class CardEditDialog(ui.dialog):
    def __init__(self, data: dict):
        super().__init__()
        self.scheme = Schema(data)
        self.keyboard = ui.keyboard(on_key=self.handle_keyboard)

        with self.props('position="right"'), ui.card().classes('w-full items-center').props('rounded'):
            with ui.element('q-list').props('bordered'):
                ui.input(label=_p('name')).bind_value(self.scheme, 'name').style('min-width:400px; max-width: 600px')
                # ui.input(label=_p('id')).bind_value(self.scheme, 'id').style('min-width:400px; max-width: 600px')
                ui.select({'add-on': _p('add-on'), 'theme': _p('theme')}, value='add-on', label=_p('type')).bind_value(
                    self.scheme, 'type')

                for k, v in self.scheme.__annotations__.items():
                    if k in ['name', 'id', 'tags', 'type', 'schema_version']:
                        continue
                    else:
                        ui.input(label=_p(k)).bind_value(self.scheme, k).style('min-width:400px; max-width: 600px')
                ui.separator()
                with ui.element('q-list').props('bordered'):
                    for k in ExtensionsOptional.__annotations__.keys():
                        if hasattr(self.scheme, k):
                            if k in ['permissions', 'platforms']: continue
                            ui.input(label=_p(k)).bind_value(self.scheme, k).style('min-width:400px; max-width: 600px')

            with ui.row():
                ui.button(_p('Cancel'), on_click=lambda: self.submit(None)).props('flat')
                ui.button(_p('Save'), on_click=lambda: self.submit(self.scheme.to_dict()))

    def handle_keyboard(self, e: events.KeyEventArguments):
        if e.key == 'Enter':
            self.submit(self.scheme.to_dict())
        elif e.key == 'Escape':
            self.submit(None)
