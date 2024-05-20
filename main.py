import sys
import nicegui
from nicegui import ui, app
from views import main_window

DEV_MODE = True

if __name__ in {"__main__", "__mp_main__"}:
    main_window.draw()
    args = {
        'title': "Blender Extension Manager",
        'reload': DEV_MODE,  # true for develop
    }

    if len(sys.argv) > 1 and "--web" in sys.argv:
        _args = {}
    else:
        _args = {
            'native': True,
            'window_size': (1280, 720),
            'frameless': True,
        }
    args.update(_args)
    ui.run(**args)
