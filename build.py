import subprocess
from pathlib import Path

APP_NAME = 'BEM'
icon_path = ''


def build_windows():
    return [
        'python',
        '-m', 'PyInstaller',
        'main.py',  # your main file with ui.run()
        '--name', APP_NAME,  # name of your app
        '--onefile',  # one file exe --ondir
        '--windowed',
        '-y',  # overwrite output folder
        # '--icon', f'{res_path().joinpath("res", "images", "icon.ico").resolve()}'
    ]


def common_data_params() -> list:
    import os
    import nicegui
    parms = [
        '--noconsole',  # 不显示控制台
        '--add-data', f'{Path(nicegui.__file__).parent}{os.pathsep}nicegui',
        # '--add-data', f'data{os.pathsep}data',  # you can add your own additional resources
        '--add-data', f'bem_statics{os.pathsep}bem_statics'  # you can add your own additional resources
    ]

    return parms


if __name__ == '__main__':
    print(build_windows())
    print(common_data_params())
    print(APP_NAME)
    print(icon_path)

    p = subprocess.Popen(build_windows() + common_data_params())
    p.communicate()
