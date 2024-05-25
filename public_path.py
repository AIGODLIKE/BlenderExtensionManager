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


def get_statics() -> Path:
    return true_path().joinpath('bme_statics')


def get_svg_str(name: str) -> Union[str, None]:
    if not name.endswith('.svg'):
        full_name = name + '.svg'
    else:
        full_name = name
    fp = get_statics().joinpath('svg',full_name)
    if not fp.exists():
        return None

    with open(fp, 'r', encoding='utf-8') as f:
        return f.read()
