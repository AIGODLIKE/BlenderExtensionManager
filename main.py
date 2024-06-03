import sys
import nicegui
from nicegui import ui, app
from views import main_window

VERSION = '0.1.1'

if __name__ in {"__main__", "__mp_main__"}:
    app.native.window_args['easy_drag'] = False
    app.storage.general['version'] = VERSION
    lang = app.storage.general.get('language', 'en_US').replace('_', '-')

    args = {
        'title': "Blender Extension Manager",
        'language': lang
    }

    if '--web' not in sys.argv:
        args.update({
            'native': True,
            'window_size': (1280, 720),
            'frameless': True,
        })
    if '--dev' in sys.argv:
        args['reload'] = True
    else:
        args['reload'] = False
    main_window.draw()
    ui.run(**args)
