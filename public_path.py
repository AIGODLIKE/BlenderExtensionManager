import os
import json
import sys
from pathlib import Path
from typing import Union
from model.config import Config

def get_b3d_ext_dir() -> Path:
    config = Config()
    version = config.data.get('blender_version','4.2')
    return Path.home().joinpath('AppData', 'Roaming', 'Blender Foundation', 'Blender', version, 'extensions')


def true_path() -> Path:
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS)
    return Path(__file__).parent


def get_bme_db() -> Path:
    return true_path().joinpath('bme_db')


def get_config():
    return get_bme_db().joinpath('config.json')

