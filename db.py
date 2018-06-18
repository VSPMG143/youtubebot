import sqlite3
from collections import namedtuple

from settings import DB_NAME


conn = sqlite3.connect(DB_NAME)
c = conn.cursor()


def create_db():
    c.execute(
        "CREATE TABLE videos (id integer primary key autoincrement, name text, "
        "url text unique, download boolean default 0, updated date default CURRENT_DATE)"
    )


def check_url(url):
    c.execute(
        "SELECT id FROM videos WHERE url = ?", (url,)
    )
    return c.rowcount == -1


def insert_row(row):
    c.execute(
        "INSERT INTO videos(name, url) VALUES (?,?)", row
    )
    conn.commit()


INSERT_ROW = "INSERT INTO videos(name, url) VALUES (?,?)"


Video = namedtuple('Video', 'name url is_download id updated')
