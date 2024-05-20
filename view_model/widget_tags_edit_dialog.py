from nicegui import ui
from translation import _p


class TagsEditDialog(ui.dialog):
    def __init__(self, tags: list):
        super().__init__()
        self.tags = tags

        def chips2list() -> list:
            return [chip.text for chip in chips if chip.value is True]

        def add_chip():
            if label_input.value == '':
                return
            if label_input.value in chips2list():
                ui.notify(_p('Tag already exists'), type='negative')
                label_input.value = ''
                return
            with chips:
                ui.chip(label_input.value, color='primary', text_color='white', removable=True)
            label_input.value = ''

        with self, ui.card().classes('w-64'):
            with ui.row().classes('gap-0') as chips:
                for tag in self.tags:
                    ui.chip(tag, color='primary', text_color='white', removable=True)

            with ui.row().classes('w-full items-center'):
                label_input = ui.input(_p('Add'))
                with label_input.add_slot('append'):
                    ui.button(icon='add', on_click=add_chip).props('round dense flat')
            with ui.row().classes('w-full items-center'):
                ui.button(_p('Cancel'), on_click=lambda: self.submit(None)).props('flat')
                ui.button(_p('Save'), on_click=lambda: self.submit(chips2list()))
