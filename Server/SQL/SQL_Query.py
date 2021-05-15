import pyodbc 
HOST = 'localhost'
DB = 'LIBRARYSOCKET'
USERNAME = 'sa'
PASSW = '1234'

cnxn = pyodbc.connect('Driver={SQL Server Native Client 11.0};'
                    'Server=' + HOST + 
                    ';Database=' + DB + 
                    ';Trusted_Connection=yes;'
                    'UID='+USERNAME +
                    ';PWD=' + PASSW)

cursor = cnxn.cursor()
cursor.execute('SELECT * FROM ACCOUNTS')

for row in cursor:
    s = str(row).split()
    print('row = ' + s[1])

class SQL_CONNECT:
    def __init__(self, HOST, DATABASE, USERNAME, PASS):
        self.cnxn = pyodbc.connect('Driver={SQL Server Native Client 11.0};'
                    'Server=' + HOST + 
                    ';Database=' + DB + 
                    ';Trusted_Connection=yes;'
                    'UID='+USERNAME +
                    ';PWD=' + PASSW)
        self.cursor = cnxn.cursor()

    def add_user(self, username, password):
        cursor.execute('SELECT * FROM ACCOUNTS \
            WHERE USERNAME =\'' + username + '\'')
        if cursor.rowcount > 0:
            return FALSE
        cursor.execute('INSERT INTO ACCOUNTS VALUE \
            (\i' + username + '\',\'' + password + '\'')
        return TRUE # Success

    def login(self, username, password):
        cursor.execute('SELECT * FROM ACCOUNTS \
            WHERE USERNAME =\'' + username + '\' + \
                AND PASSW = \'' + password + '\i')
        if cursor.rowcount > 0:
            return True 
        return False

    
            