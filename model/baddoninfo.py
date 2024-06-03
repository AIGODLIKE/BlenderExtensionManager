import re
from pathlib import Path
from typing import Optional, Union
from .schema import Schema

"""
    "name": "New Object",
    "author": "Your Name Here",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Add > Mesh > New Object",
    "description": "Adds a new Mesh Object",
    "warning": "",
    "doc_url": "",
    "url":"",
    "category": "Add Mesh",
"""


class BAddonInfo:
    name: str
    author: str
    blender: tuple[int, int, int]
    version: Union[tuple[int, int], tuple[int, int, int]]
    location: str
    description: str
    category: str
    warnings: Optional[str]
    doc_url: Optional[str]
    url: Optional[str]

    def setup(self, path: Path) -> tuple[bool, Union[dict, str]]:
        """setup the bl_info from the __init__.py file of the addon
        :param
            path (Path): The path/directory to the __init__.py file of the addon
        :return
            (bool, Union[dict, str]) - (True, bl_info) if bl_info is found, else (False, 'bl_info not found')
        """
        self.path = path
        res, data = self.get_bl_addon_info(path)
        if not res: return (res, data)
        for k, v in data.items():
            if k in self.__annotations__:
                setattr(self, k, v)
        return (res, data)

    @staticmethod
    def version_fix(v: tuple) -> str:
        """fix version to fit the schema version format"""
        if len(v) == 2:
            v = (*v, 0)
        return '.'.join(map(str, v))

    @property
    def fix_version(self) -> str:
        """schema version must be 3 digits, so we need to fix it here."""
        return self.version_fix(self.version)

    @property
    def fix_blender_version(self) -> str:
        """schema version must be 3 digits, so we need to fix it here."""
        return self.version_fix(self.blender)

    def to_schema_data(self) -> dict:
        """convert the bl_info to schema valid data
        :return: dict
        """
        if self.path.name == '__init__.py':
            ID = self.path.parent.name
        else:
            ID = self.path.name
        if not getattr(self, 'url', None) or self.url == '':
            self.url = 'https://blender.org'
        if not getattr(self, 'description', None) or self.description == '':
            self.description = 'A Blender Add-on'

        data = {
            'name': self.name,
            'id': ID,
            'maintainer': self.author,
            'version': self.fix_version,
            'tagline': self.description,
            'blender_version_min': self.fix_blender_version,
            'type': 'add-on',
            'schema_version': '1.0.0',
            'tags': [self.category, ],
            'license': ['license', ],
            'website': self.url,
        }

        return data

    @staticmethod
    def get_bl_addon_info(filepath: Union[Path,]) -> tuple[bool, Union[dict, str]]:
        """Get the bl_info from the __init__.py file of the addon
        Args:
            filepath (Union[Path,]): The path/directory to the __init__.py file of the addon
        :return: (bool, Union[dict, str]) - (True, bl_info) if bl_info is found, else (False, 'bl_info not found')
        """
        if filepath.is_dir():
            fp = filepath.joinpath('__init__.py')
        else:
            fp = filepath

        rule = re.compile(r'bl_info\s*=\s*{.*?}', re.DOTALL)
        with open(fp, 'r', encoding='utf-8') as f:
            _bl_info = rule.findall(f.read())

        if not _bl_info:
            return (False, 'bl_info not found')
        bl_info = eval(_bl_info[0].split('=')[1])

        return (True, bl_info)
