import os
import json
import sys
from pathlib import Path
from typing import Union


def true_path() -> Path:
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS)
    return Path(__file__).parent


def get_bme_db() -> Path:
    return true_path().joinpath('bme_db')



