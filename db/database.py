from contextlib import contextmanager
from pathlib import Path
import sqlite3
BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE = BASE_DIR / 'data' / 'legacy.sqlite3'

@contextmanager
def connect(path=DATABASE):
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute('PRAGMA foreign_keys = ON')
    try:
        with connection:
            yield connection
    finally:
        connection.close()
