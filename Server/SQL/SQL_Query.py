import pyodbc 

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
        user = cursor.execute('SELECT * FROM ACCOUNTS \
            WHERE USERNAME =\'?\'', username).fetchall()
        if len(user) > 0:
            return FALSE
        cursor.execute('INSERT INTO ACCOUNTS VALUE \
            (\'?\',\'?\'', username, password)
        return TRUE # Success

    def login(self, username, password):
        user = cursor.execute('SELECT * FROM ACCOUNTS \
            WHERE USERNAME =\'?\' + \
                AND PASSW = \'?\'', username, password).fetchall()
        if user > 0:
            return True 
        return False

    def getlist(self, searchtype, value):
        field = None
        if searchtype == ID:
            field = 'ID'
        if searchtype == 'Name':
            field = 'BOOK_NAME'
        if searchtype == 'Type':
            field = 'CATEGORY'
        
        if (field):
            books = cursor.execute('SELECT * FROM BOOKS \
            WHERE ?=\'?\'', field, value).fetchall()
            return books[:][:-1]
        else:
            books = cursor.execute('SELECT * FROM BOOKS \
            WHERE AUTHORS =\'%?%\'', value).fetchall()
            return books[:][:-1]

    '''
    def sql_to_dictionary(self, cursor):
        if cursor.rowcount == 0:
            return None
        book = []
        for row in cursor:
            s = str(row)
            s = s[1:]
            s = s[:-1]
            info = s.split(',')
            info.pop(5) # remove link from info
            book.append(info)
        return book
        '''

    def get_book_link(self, ID):
        book = cursor.execute('SELECT * FROM BOOKS \
            WHERE ID =\'?\'', ID).fetchall()
        # should cursor.rowcount shold be > 0
        return book[0][5]


    
            