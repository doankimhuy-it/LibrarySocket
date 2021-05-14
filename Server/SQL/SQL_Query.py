import mysql.connector
HOST = '127.0.0.1'
DB = 'LIBRARYSOCKET'
USERNAME = 'sa'
PASSW = '1234'
conn = mysql.connector.connect(user=USERNAME, password=PASSW, host = HOST, database= DB)
cursor = conn.cursor()
cursor.execute("SELECT DATABASE()")
data = cursor.fetchone()
print("Connection established to: ",data)
conn.close()
