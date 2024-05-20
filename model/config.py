import json
from public_path import get_bme_db
from nicegui import app


class Config:
    data: dict

    def __init__(self):
        self._load()

    def _load(self):
        fp = get_bme_db().joinpath('config.json')
        if not fp.exists():
            self.data = {}
            return
        with open(fp, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

    def _save(self):
        fp = get_bme_db().joinpath('config.json')
        with open(fp, 'w', encoding='utf-8') as f:
            json.dump(self.data, f)
