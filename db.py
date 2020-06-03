import sqlite3
import os
from typing import Tuple, List


class Error(Exception):
    pass


conn: sqlite3.Connection
c: sqlite3.Cursor


def open_db() -> int:
    """
        Открытие БД.
        Если БД не существует, будет создана новая БД.
    """
    global conn
    global c

    try:
        if os.path.exists('authentication/service'):
            conn = sqlite3.connect('authentication/service/database.db')
            c = conn.cursor()
        else:
            os.mkdir('authentication/service')
            conn = sqlite3.connect('authentication/service/database.db')
            c = conn.cursor()
        return 0
    except sqlite3.Error as e:
        raise Error("Error in db.open_db(): " + str(e))


def close_db() -> int:
    global conn
    try:
        conn.close()
        return 0
    except sqlite3.Error as e:
        raise Error("Error in db.close_db(): " + str(e))


def create_table() -> int:
    """
        Создание таблицы, если она не существует.
    """
    global conn
    global c

    try:
        with conn:
            c.execute("""
                CREATE TABLE IF NOT EXISTS users (
                login       TEXT        PRIMARY KEY NOT NULL UNIQUE, \
                hash        BLOB        NOT NULL, \
                dir         TEXT        NOT NULL UNIQUE, \
                enc_key     BLOB        NOT NULL, \
                iv          BLOB        NOT NULL
                )
            """)
        return 0
    except sqlite3.Error as e:
        raise Error("Error in db.create_table(): " + str(e))


def insert(login: str, hash: bytes, dir: str,
           enc_key: bytes, iv: bytes) -> int:
    global conn
    global c
    if not isinstance(login, str) or not isinstance(hash, bytes) \
            or not isinstance(dir, str) or not isinstance(enc_key, bytes) \
            or not isinstance(iv, bytes):
        raise Error("Error in db.insert(): Incorrect login type")
    if len(login) < 1:
        raise Error("Error in db.insert(): Incorrect login length")
    if login == 'None':
        raise Error(
            f"Error in db.insert(): You can not use {login} as a login")
    try:
        with conn:
            c.execute("""
                INSERT INTO users (login, hash, dir, enc_key, iv) \
                VALUES (?, ?, ?, ?, ?)""",
                      (login, hash, dir, enc_key, iv))
        return 0
    except sqlite3.IntegrityError as e:
        raise Error("Error in db.insert(): " + str(e))


def cut(login: str) -> int:
    global conn
    global c
    if not isinstance(login, str):
        raise Error("Error in db.cut(): Incorrect login type")
    if len(login) < 1:
        raise Error("Error in db.cut(): Incorrect login length")

    with conn:
        c.execute("""SELECT * FROM users WHERE login=?""", (login, ))
        info: Tuple[str, bytes, str, bytes] = c.fetchone()
        if info is None:
            raise Error("Error in db.cut(): Incorrect login")

    try:
        with conn:
            c.execute("""DELETE FROM users WHERE login=?""", (login, ))
        return 0
    except sqlite3.IntegrityError as e:
        raise Error("Error in db.cut(): " + str(e))


def update(login: str = 'None', hash: bytes = b'None',
           dir: str = 'None', enc_key: bytes = b'None',
           iv: bytes = b'None') -> int:
    global conn
    global c

    if login == 'None':
        raise Error("Error in db.update(): Login not specified")

    try:
        with conn:
            c.execute("""SELECT * FROM users WHERE login=?""", (login, ))
            if c.fetchone() is None:
                raise Error(
                    f"Error in db.update(): User with login {login} not found")
    except sqlite3.IntegrityError as e:
        raise Error("Error in db.update(): " + str(e))

    temp_values: List[object] = [
        login, hash, dir, enc_key, iv]
    temp_types: List[object] = [
        str, bytes, str, bytes, bytes]

    for i in range(len(temp_values)):
        if not isinstance(temp_values[i], temp_types[i]):
            raise Error("Error in db.update(): Incorrect data type")
        if len(temp_values[i]) < 1:
            raise Error("Error in db.update(): Incorrect data length")

    try:
        with conn:
            if hash != b'None':
                c.execute("""
                UPDATE users SET hash=? WHERE login=?""", (hash, login))
            if dir != 'None':
                c.execute("""
                UPDATE users SET dir=? WHERE login=?""", (dir, login))
            if enc_key != b'None':
                c.execute("""
                UPDATE users SET enc_key=? WHERE login=?""", (enc_key, login))
            if iv != b'None':
                c.execute("""
                UPDATE users SET iv=? WHERE login=?""", (iv, login))
        return 0
    except sqlite3.IntegrityError as e:
        raise Error("Error in db.update(): " + str(e))


def info(login: str) -> Tuple[str, bytes, str, bytes, bytes]:
    if not isinstance(login, str):
        raise Error("Error in db.info(): Invalid input type")
    global conn
    global c
    try:
        with conn:
            c.execute("""SELECT * FROM users WHERE login=?""", (login, ))
            info: Tuple[str, bytes, str, bytes, bytes] = c.fetchone()
    except sqlite3.IntegrityError as e:
        raise Error("Error in db.info(): " + str(e))
    if not isinstance(info[0], str) or not isinstance(info[1], bytes) \
            or not isinstance(info[2], str) or not isinstance(info[3], bytes) \
            or not isinstance(info[4], bytes):
        raise Error("Error in db.info(): Invalid output type")
    return info
