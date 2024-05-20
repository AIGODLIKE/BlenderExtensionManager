import sys
from nicegui import ui, app
from views import main_window

if __name__ in {"__main__", "__mp_main__"}:
    main_window.draw()
    if len(sys.argv) > 1 and sys.argv[1] == "--web":
        ui.run()
    else:
        ui.run(native=True, window_size=(1280, 720),frameless=True, title="Blender Extension Manager")
