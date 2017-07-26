import sqlite3


conn = sqlite3.connect('youtube.db')
c = conn.cursor()

c.execute('''CREATE TABLE videos
             (id int primary key, name text, url text unique)''')
