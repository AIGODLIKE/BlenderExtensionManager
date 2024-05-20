from nicegui import app
from model.config import Config
from .zh_CN import data as zh_CN

data = {}
en_US = dict(zip(zh_CN.keys(), zh_CN.keys()))
data.update({
    'zh_CN': zh_CN,
})

config = Config()


def _p(text: str) -> str:
    """return the translation of the text"""
    lang = config.data['language']

    d = data.get(lang, 'en_US')
    if d == 'en_US': return text
    return d.get(text, text)
