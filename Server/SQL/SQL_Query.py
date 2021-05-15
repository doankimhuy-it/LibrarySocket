import sqlite3
HOST = 'localhost'
DB = 'LIBRARYSOCKET'
USERNAME = 'sa'
PASSW = '1234'
print(1)
conn = sqlite3.connect(user=USERNAME, password=PASSW, host = HOST, port=5939, database= DB)
print(2)
cursor = conn.cursor()
cursor.execute("SELECT USERNAME FROM ACCOUNTS")
data = cursor.fetchone()
print("Connection established to: ",data)
conn.close()
