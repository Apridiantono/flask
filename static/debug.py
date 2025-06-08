import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM kelas")
data = cursor.fetchall()

for row in data:
    print(row)

conn.close()
