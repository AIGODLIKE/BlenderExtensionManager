import re
from pathlib import Path


class Blender():
    path: str
    is_valid: bool
    # info
    version_str: str
    version: str # x.x.x
    date: str
    hash: str
    date: str

    def init_from_str(self, version_str: str):
        # find and set attr from s
        # s example: Blender 4.1.1 (hash e1743a0317bc built 2024-04-15 23:33:30)
        self.version_str = version_str
        m = re.search(r'(\d+)\.(\d+)\.(\d+)', version_str)
        if m:
            self.version = ".".join([m.group(1), m.group(2), m.group(3)])
        m = re.search(r'built (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', version_str)
        if m:
            self.date = m.group(1)
        m = re.search(r'hash ([a-f0-9]+)', version_str)
        if m:
            self.hash = m.group(1)

        if self.version and self.date and self.hash:
            self.is_valid = True
        return self.is_valid
