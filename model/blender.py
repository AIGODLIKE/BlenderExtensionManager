import re
import sqlite3
from pathlib import Path
from contextlib import contextmanager
from public_path import get_bme_db


@contextmanager
def open_db(db_path: Path) -> tuple[sqlite3.Connection, sqlite3.Cursor]:
    conn = sqlite3.connect(str(db_path))
    yield conn, conn.cursor()
    conn.close()


class Blender():
    path: str = ''
    is_valid: bool
    # info
    version_str: str
    version: str  # x.x.x
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

    @property
    def db_path(self):
        return get_bme_db().joinpath('blender.db')

    def update_db(self):
        with open_db(self.db_path) as (conn, c):
            # 查询blenders表中是否存在当前Blender实例的记录
            c.execute("SELECT * FROM blenders WHERE path = ?", (self.path,))
            row = c.fetchone()

            if row is None:
                # 如果不存在，则保存
                self._save_to_db()
            else:
                # 如果存在，则更新
                self._update_db()

    def _save_to_db(self):
        with open_db(self.db_path) as (conn, c):
            c.execute('''
                        CREATE TABLE IF NOT EXISTS blenders
                        (path text, is_valid integer, version_str text, version text, date text, hash text)
                    ''')

            c.execute("INSERT INTO blenders VALUES (?, ?, ?, ?, ?, ?)",
                      (self.path,
                       int(self.is_valid),
                       self.version_str,
                       self.version,
                       self.date,
                       self.hash))
            conn.commit()

    def _update_db(self):
        with open_db(self.db_path) as (conn, c):
            # 更新blenders表中的记录
            c.execute("""
                UPDATE blenders
                SET is_valid = ?, version_str = ?, version = ?, date = ?, hash = ?
                WHERE path = ?
            """, (int(self.is_valid), self.version_str, self.version, self.date, self.hash, self.path))
            conn.commit()

    def load_from_db(self) -> bool:
        with open_db(self.db_path) as (conn, c):
            c.execute("SELECT * FROM blenders WHERE path=?", (self.path,))
            row = c.fetchone()
            if row:
                self.path, is_valid, self.version_str, self.version, self.date, self.hash = row
                self.is_valid = bool(is_valid)
                return True
            return False
