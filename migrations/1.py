from db import conn


c = conn.cursor()

def add_date_column():
    c.execute("alter table videos add column 'create_at' 'datetime default current_timestamp'")
  
  
if __name__ == "__main__":
    add_date_column()
  
