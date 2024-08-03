import sqlite3

conn = sqlite3.connect('reviews.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS reviews
             (question TEXT, answer TEXT, review INTEGER)''')
conn.commit()
conn.close()
