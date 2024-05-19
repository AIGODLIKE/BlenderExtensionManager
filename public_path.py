import os
import json
from pathlib import Path
from typing import Union


def get_b3d_ext_dir(version: str = '4.2') -> Path:
    return Path.home().joinpath('AppData', 'Roaming', 'Blender Foundation', 'Blender', version, 'extensions')



