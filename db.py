import sqlite3


conn = sqlite3.connect('youtube.sqlite3')
c = conn.cursor()

def create_db():
	c.execute('''CREATE TABLE videos
              (id int primary key, name text, url text unique)''')
