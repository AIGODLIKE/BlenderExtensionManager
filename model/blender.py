import re
import sqlite3
import json
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
    is_active: bool = False
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

    @staticmethod
    def db_path() -> Path:
        return get_bme_db().joinpath('blender.db')

    def save_to_db(self):
        with open_db(self.db_path()) as (conn, c):
            # 查询blenders表中是否存在当前Blender实例的记录
            try:
                c.execute("SELECT * FROM blenders WHERE path = ?", (self.path,))
                row = c.fetchone()
            except sqlite3.OperationalError:
                row = None
            if row is None:
                # 如果不存在，则保存
                self.init_db()
            else:
                # 如果存在，则更新
                self._update_db()

    def remove_from_db(self):
        with open_db(self.db_path()) as (conn, c):
            c.execute("DELETE FROM blenders WHERE path=?", (self.path,))
            conn.commit()

    def init_db(self):
        with open_db(self.db_path()) as (conn, c):
            column_str = ''
            set_values = []
            for name in self.__annotations__.keys():
                if isinstance(getattr(self, name), bool):
                    column_str += f"{name} integer, "
                    set_values.append(int(getattr(self, name)))
                elif isinstance(getattr(self, name), str):
                    column_str += f"{name} text, "
                    set_values.append(getattr(self, name))

            # 移除最后的逗号和空格
            column_str = column_str.rstrip(', ')

            c.execute(f'''
                        CREATE TABLE IF NOT EXISTS blenders
                        ({column_str})
                    ''')

            # 根据set_values的长度动态生成问号的数量
            placeholders = ', '.join('?' * len(set_values))
            c.execute(f"INSERT INTO blenders VALUES ({placeholders})",
                      (*set_values,))
            conn.commit()

    def _update_db(self):
        with open_db(self.db_path()) as (conn, c):
            # 更新blenders表中的记录
            set_str = ', '.join([f"{column} = ?" for column in self.__annotations__.keys() if column != 'path'])
            set_values = [
                (int(getattr(self, column)) if isinstance(getattr(self, column), bool) else getattr(self, column)) for
                column in self.__annotations__.keys() if column != 'path']

            c.execute(f"""
                UPDATE blenders
                SET {set_str}
                WHERE path = ?
            """, (*set_values, self.path))
            conn.commit()

    @staticmethod
    def is_path_in_db(path) -> bool:
        with open_db(Blender.db_path()) as (conn, c):
            try:
                c.execute("SELECT * FROM blenders WHERE path=?", (path,))
                row = c.fetchone()
            except:
                row = None
            if row:
                return True
            return False

    @staticmethod
    def load_all_from_db() -> list['Blender']:
        with open_db(Blender.db_path()) as (conn, c):
            blenders = []
            # if table not exists, return empty list
            try:
                c.execute("SELECT * FROM blenders")

            except:
                return blenders
            # get column
            column_names = [description[0] for description in c.description]

            rows = c.fetchall()
            for row in rows:
                blender = Blender()
                for i, column_name in enumerate(column_names):
                    if column_name in ['is_valid', 'is_active']:
                        value = bool(row[i])
                    else:
                        value = row[i]
                    setattr(blender, column_name, value)
                blenders.append(blender)
            return blenders
