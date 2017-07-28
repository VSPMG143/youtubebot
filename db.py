import sqlite3


conn = sqlite3.connect('youtube.sqlite3')
c = conn.cursor()

def create_db():
	c.execute(
		"CREATE TABLE videos (id integer primary key autoincrement, name text, url text unique)"
	)

def check_url(url):
	c.execute(
		"SELECT id FROM videos WHERE url = ?", url
	)

def insert_row(row):
    c.execute(
        "INSERT INTO videos VALUES (?,?,?)", row
    )
