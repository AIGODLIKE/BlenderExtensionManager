import sys
import nicegui
from nicegui import ui, app
from views import main_window

if __name__ in {"__main__", "__mp_main__"}:
    app.native.window_args['easy_drag'] = False
    args = {'title': "Blender Extension Manager", }

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
