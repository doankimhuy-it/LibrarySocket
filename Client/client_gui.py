# Python GUI
import sys
from PySide6 import QtCore, QtWidgets, QtGui
import logging
from enum import Enum, auto
import operator

logging.basicConfig(level=logging.DEBUG)


class ClientWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.timer_update_GUI = QtCore.QTimer()

        # create windows title and its size
        self.setWindowTitle("Client")
        self.setFixedSize(600, 300)

        # IP box
        self.IP_textbox = QtWidgets.QLineEdit("127.0.0.1", self)
        self.IP_textbox.move(20, 20)
        self.IP_textbox.setFixedWidth(200)

        # Port box
        self.port_textbox = QtWidgets.QLineEdit("65432", self)
        self.port_validator = QtGui.QIntValidator(0, 65535, self)
        self.port_textbox.setValidator(self.port_validator)
        self.port_textbox.move(240, 20)
        self.port_textbox.setFixedWidth(70)

        # Connect button
        self.connect_button = QtWidgets.QPushButton("Connect!", self)
        self.connect_button.move(330, 20)
        self.connect_button.setFixedWidth(110)

        # Connect status
        self.connect_status_box = QtWidgets.QLabel("DISCONNECTED!", self, alignment=QtCore.Qt.AlignCenter)
        self.connect_status_box.move(460, 20)
        self.connect_status_box.setFixedWidth(120)
        self.connect_status_box.setStyleSheet("border: 1.5px solid black; font-weight: bold; color : red;")

        # Login/Logout group box
        self.login_groupbox = QtWidgets.QGroupBox("Login/Sign up", self)
        self.login_groupbox.move(10, 60)
        self.login_groupbox.setFixedSize(580, 220)

        self.login_layout = QtWidgets.QGridLayout(self.login_groupbox)

        # Username box
        self.label_username = QtWidgets.QLabel("Username:", self.login_groupbox)
        self.label_username.setStyleSheet('font-size: 16px')
        self.username_textbox = QtWidgets.QLineEdit(self.login_groupbox)
        self.username_regex = QtCore.QRegularExpression("[A-Za-z0-9._]+")
        self.username_validator = QtGui.QRegularExpressionValidator(self.username_regex)
        self.username_textbox.setValidator(self.username_validator)
        self.username_textbox.setFixedSize(300, 30)
        self.login_layout.addWidget(self.label_username, 0, 0)
        self.login_layout.addWidget(self.username_textbox, 0, 1)

        # Password box
        self.label_password = QtWidgets.QLabel("Password:", self.login_groupbox)
        self.label_password.setStyleSheet('font-size: 16px')
        self.password_textbox = QtWidgets.QLineEdit(self.login_groupbox)
        self.password_regex = QtCore.QRegularExpression("[^-\s]+")
        self.password_validator = QtGui.QRegularExpressionValidator(self.password_regex)
        self.password_textbox.setValidator(self.password_validator)
        self.password_textbox.setFixedSize(300, 30)
        self.password_textbox.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login_layout.addWidget(self.label_password, 1, 0)
        self.login_layout.addWidget(self.password_textbox, 1, 1)

        # Sign-up button
        self.signup_button = QtWidgets.QPushButton("No account?\nSIGN UP", self.login_groupbox)
        self.signup_button.setFixedSize(100, 60)
        self.signup_button.setStyleSheet('color: red; font-size: 14px;')
        self.login_layout.addWidget(self.signup_button, 2, 0)

        # Login button
        self.login_button = QtWidgets.QPushButton("LOGIN", self.login_groupbox)
        self.login_button.setFixedSize(160, 60)
        self.login_button.setStyleSheet('font-size: 16px; font-weight: bold; color: green;')
        self.login_layout.addWidget(self.login_button, 2, 1, QtCore.Qt.AlignCenter)

        self.login_groupbox.setLayout(self.login_layout)

        # Book group box
        self.book_groupbox = QtWidgets.QGroupBox("Book browsing", self)
        self.book_groupbox.move(10, 60)
        self.book_groupbox.setFixedSize(580, 230)

        self.main_widget = QtWidgets.QTableView(self.book_groupbox)
        self.main_widget.move(5, 50)
        self.main_widget.setFixedSize(570, 175)
        self.main_widget.setSortingEnabled(True)
        self.main_widget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.main_widget.setSelectionBehavior(QtWidgets.QTableView.SelectRows)

        self.book_combobox = QtWidgets.QComboBox(self.book_groupbox)
        self.book_combobox.addItems(['F_ID', 'F_Name', 'F_Type', 'F_Author'])
        self.book_combobox.move(5, 20)

        self.book_info_textbox = QtWidgets.QLineEdit(self.book_groupbox)
        self.book_info_textbox.setFixedWidth(160)
        self.book_info_textbox.setPlaceholderText("Enter string to search")
        self.book_info_textbox.move(85, 20)

        self.search_button = QtWidgets.QPushButton("Search", self.book_groupbox)
        self.search_button.move(250, 19)
        self.search_button.setStyleSheet('color: green;')
        self.search_button.setFixedWidth(60)

        self.view_button = QtWidgets.QPushButton("View book", self.book_groupbox)
        self.view_button.move(315, 19)

        self.download_button = QtWidgets.QPushButton("Download book", self.book_groupbox)
        self.download_button.move(395, 19)
        self.download_button.setFixedWidth(100)

        self.logout_button = QtWidgets.QPushButton("LOGOUT!", self.book_groupbox)
        self.logout_button.move(500, 19)
        self.logout_button.setStyleSheet('color: red;')

        self.login_groupbox.setVisible(False)
        self.book_groupbox.setVisible(False)

    @QtCore.Slot()
    def MessageError(self, message, title = 'Error', width = None, info_icon = None):
        message_box = QtWidgets.QMessageBox(self)
        message_box.setText(message)
        message_box.setWindowTitle(title)
        if width:
            message_box.setFixedWidth(width)
        if info_icon:
            message_box.setIcon(QtWidgets.QMessageBox.Information)
        message_box.exec_()

    def get_username_password(self):
        username = self.username_textbox.text()
        password = self.password_textbox.text()
        if (len(username) < 6) or (len(password) < 4):
            mess = 'Username must be longer than 5 characters\nPassword must be longer than 3 charaters \
                        \nRe-enter information to continue'
            title = 'Username/Password error'
            self.MessageError(mess, title, width = 200, info_icon=True)
            return [None, None]
        return [username, password]
        
    def value_to_search(self):
        value = self.book_info_textbox.text()
        search_type = self.book_combobox.currentText()
        if len(value) == 0:
            self.MessageError('No value to search')
            return [None, None]
        return [search_type[2:], value]

    def ID_selected_book(self):
        index = self.main_widget.selectedIndexes()
        if not index:
            logging.debug('No book selected')
            self.MessageError('Select a book to view')
            return None
        row = index[0].row()
        ID = self.main_widget.model().index(row, 0).data()
        return ID

    def show_book_content(self, book_content):
        view_diag = QtWidgets.QDialog(self)
        view_diag.setWindowTitle('Book content')
        view_diag.setFixedSize(400, 400)

        book_content_dialog = QtWidgets.QTextEdit(view_diag)
        book_content_dialog.move(10, 10)
        book_content_dialog.setFixedSize(380, 380)
        book_content_dialog.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        book_content_dialog.setReadOnly(True)
        book_content_dialog.setWordWrapMode(QtGui.QTextOption.WordWrap)

        book_content_dialog.setText(book_content)
        view_diag.show()

    def add_click_behavior(self, obj, func):
        obj.clicked.connect(func)

    def change_GUI_status(self, ConnectStatusCode, LoginStatusCode=0):
        if ConnectStatusCode == self.ConnectStatusCode.CONNECTING:
            ConnectingString = ['Connecting', 'Connecting.', 'Connecting..', 'Connecting...']
            text = self.connect_button.text()
            index = 3
            if (text != 'Connect!'):
                index = ConnectingString.index(text)
            index = (index + 1) % 4
            self.connect_button.setText(ConnectingString[index])
            self.login_groupbox.setVisible(False)
            self.book_groupbox.setVisible(False)

        if ConnectStatusCode == self.ConnectStatusCode.CONNECTED:
            self.connect_button.setText('Disconnect!')
            self.connect_status_box.setText('CONNECTED!')
            self.connect_status_box.setStyleSheet("border: 1.5px solid black; font-weight: bold; color: green;")

            if LoginStatusCode == self.LoginStatusCode.LOGGED_IN:
                self.login_groupbox.setVisible(False)
                self.book_groupbox.setVisible(True)
            elif LoginStatusCode == self.LoginStatusCode.LOGGED_OUT:
                self.login_groupbox.setVisible(True)
                self.book_groupbox.setVisible(False)

        if ConnectStatusCode == self.ConnectStatusCode.DISCONNECTED:
            self.connect_button.setText('Connect!')
            self.connect_status_box.setText('DISCONNECTED!')
            self.connect_status_box.setStyleSheet("border: 1.5px solid black; font-weight: bold; color: red;")
            self.login_groupbox.setVisible(False)
            self.book_groupbox.setVisible(False)

        if ConnectStatusCode == self.ConnectStatusCode.TIMEOUT:
            self.connect_button.setText('Connect!')
            self.connect_status_box.setText('TIMED OUT!')
            self.connect_status_box.setStyleSheet("border: 1.5px solid black; font-weight: bold; color: brown;")
            self.login_groupbox.setVisible(False)
            self.book_groupbox.setVisible(False)

    def list_book_to_table(self, book_dict):
        header = ['ID', 'Name', 'Category', 'Authors', 'Release year']
        books_with_header = list(book_dict.values())
        book_list = []
        for book in books_with_header:
            book['ID'] = str(book['ID'])
            book['Release year'] = str(book['Release year'])
            book_list.append(list(book.values()))
        model = TableModel(self, book_list, header)
        self.main_widget.setModel(model)
        self.main_widget.setColumnWidth(0, 10)
        return book_list

    class ConnectStatusCode(Enum):
        CONNECTED = auto(),
        DISCONNECTED = auto(),
        CONNECTING = auto(),
        TIMEOUT = auto()

    class LoginStatusCode(Enum):
        LOGGED_IN = auto(),
        LOGGED_OUT = auto()


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent, mylist, header, *args):
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        self.mylist = mylist
        self.header = header

    def rowCount(self, parent):
        return len(self.mylist)

    def columnCount(self, parent):
        return len(self.mylist[0])

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role != QtCore.Qt.DisplayRole:
            return None
        return self.mylist[index.row()][index.column()]

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.header[col]
        else:
            return QtCore.QAbstractTableModel.headerData(self, col, orientation, role)

    def sort(self, col, order):
        self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
        self.mylist = sorted(self.mylist, key=operator.itemgetter(col))
        if order == QtCore.Qt.DescendingOrder:
            self.mylist.reverse()
        self.emit(QtCore.SIGNAL("layoutChanged()"))


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    window = ClientWindow()
    window.show()

    sys.exit(app.exec_())
