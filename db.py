import sqlite3

from settings import DB_NAME


conn = sqlite3.connect(DB_NAME)
c = conn.cursor()

def create_db():
	c.execute(
		"CREATE TABLE videos (id integer primary key autoincrement, name text, url text unique)"
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
