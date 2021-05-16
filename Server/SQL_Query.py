import pyodbc 

class SQL_CONNECT:
    def __init__(self, HOST, DATABASE, USERNAME, PASSW):

        self.cnxn = pyodbc.connect('Driver={SQL Server Native Client 11.0};'
                    'Server=' + HOST + 
                    ';Database=' + DATABASE + 
                    ';Trusted_Connection=yes;'
                    'UID='+USERNAME +
                    ';PWD=' + PASSW)

        self.cursor = self.cnxn.cursor()

    def add_user(self, username, password):
        user = self.cursor.execute('SELECT * FROM ACCOUNTS \
            WHERE USERNAME =?', username).fetchall()

        if len(user) > 0:
            return False
        self.cursor.execute('INSERT INTO ACCOUNTS(USERNAME, PASSW) VALUES \
            (?,?)', username, password)
        self.cnxn.commit()
        return True # Success

    def login(self, username, password):
        user = self.cursor.execute('SELECT * FROM ACCOUNTS \
            WHERE USERNAME =? \
                AND PASSW = ?', username, password).fetchall()
        if len(user) > 0:
            return True 
        return False

    def get_list_book(self, searchtype, value):
        field = None
        if searchtype == 'ID':
            field = 'ID'
        if searchtype == 'Name':
            field = 'BOOK_NAME'
        if searchtype == 'Type':
            field = 'CATEGORY'
        
        if (field != None):
            books = self.cursor.execute('SELECT ID, BOOK_NAME, CATEGORY, AUTHORS, RELEASEYEAR FROM BOOKS \
            WHERE ' + field + ' = ?', value).fetchall()
            return books
        else:
            value = '%' + value + '%'
            books = self.cursor.execute('SELECT ID, BOOK_NAME, CATEGORY, AUTHORS, RELEASEYEAR FROM BOOKS \
            WHERE AUTHORS LIKE ?', value).fetchall()
            return books

    def list_user(self):
        users = self.cursor.execute('SELECT * FROM ACCOUNTS').fetchall()
        for user in users:
            print(user[0], user[1])

    def get_book_link(self, ID):
        book = self.cursor.execute('SELECT LINK FROM BOOKS \
            WHERE ID =?', ID).fetchall()
        # should cursor.rowcount shold be > 0
        return book

if __name__ == '__main__':
    x = SQL_CONNECT('localhost', 'LIBRARYSOCKET', 'sa', '1234')
    print(x.get_list_book('ID', 1))
    print(x.get_book_link(1))
            