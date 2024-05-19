from .zh_CN import data as zh_CN

data = {}
data.update({
    'zh_CN': zh_CN,
})


def _p(text: str, lang: str = 'zh_CN') -> str:
    """return the translation of the text"""
    d = data.get(lang, None)
    if not d: return text
    return d.get(text, text)
