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
        self.setFixedSize(500, 300)

        # IP box
        self.IPTextBox = QtWidgets.QLineEdit("127.0.0.1", self)
        self.IPTextBox.move(20, 20)
        self.IPTextBox.setFixedWidth(200)

        # Port box
        self.PortTextBox = QtWidgets.QLineEdit("65432", self)
        self.PortValidator = QtGui.QIntValidator(0, 65535, self)
        self.PortTextBox.setValidator(self.PortValidator)
        self.PortTextBox.move(self.IPTextBox.geometry().x() + self.IPTextBox.width() + 5, 20)
        self.PortTextBox.setFixedWidth(50)

        # Connect button
        self.ConnectButton = QtWidgets.QPushButton("Connect!", self)
        self.ConnectButton.move(self.PortTextBox.geometry().x() + self.PortTextBox.width() + 5, 20)

        # Connect status
        self.ConnectStatusBox = QtWidgets.QLabel("DISCONNECTED!", self, alignment=QtCore.Qt.AlignCenter)
        self.ConnectStatusBox.move(10 + self.ConnectButton.geometry().x() + self.ConnectButton.width(), 20)
        self.ConnectStatusBox.setStyleSheet("border: 1.5px solid black; font-weight: bold; color : red;")

    def login_gui(self, isEnabled):
        # Login/Logout group box
        self.LogGroupBox = QtWidgets.QGroupBox("Login/Sign up", self)
        self.LogGroupBox.move(20, 60)
        self.LogGroupBox.setFixedSize(460, 220)

        self.LogLayout = QtWidgets.QGridLayout(self.LogGroupBox)

        # Username box
        self.label_username = QtWidgets.QLabel("Username:", self.LogGroupBox)
        self.label_username.setStyleSheet('font-size: 16px')
        self.UsernameBox = QtWidgets.QLineEdit(self.LogGroupBox)
        self.UsernameRegex = QtCore.QRegularExpression("[A-Za-z0-9._]+")
        self.UsernameValidator = QtGui.QRegularExpressionValidator(self.UsernameRegex)
        self.UsernameBox.setValidator(self.UsernameValidator)
        self.UsernameBox.setFixedSize(250, 30)
        self.LogLayout.addWidget(self.label_username, 0, 0)
        self.LogLayout.addWidget(self.UsernameBox, 0, 1)

        # Password box
        self.label_password = QtWidgets.QLabel("Password:", self.LogGroupBox)
        self.label_password.setStyleSheet('font-size: 16px')
        self.PasswordBox = QtWidgets.QLineEdit(self.LogGroupBox)
        self.PasswordRegex = QtCore.QRegularExpression("[^-\s]+")
        self.PasswordValidator = QtGui.QRegularExpressionValidator(self.PasswordRegex)
        self.PasswordBox.setValidator(self.PasswordValidator)
        self.PasswordBox.setFixedSize(250, 30)
        self.LogLayout.addWidget(self.label_password, 1, 0)
        self.LogLayout.addWidget(self.PasswordBox, 1, 1)

        # Sign-up button
        self.SignupButton = QtWidgets.QPushButton("No account?\nSIGN UP", self.LogGroupBox)
        self.SignupButton.setFixedSize(100, 60)
        self.SignupButton.setStyleSheet('color: red; font-size: 14px;')
        self.LogLayout.addWidget(self.SignupButton, 2, 0)

        # Login button
        self.LoginButton = QtWidgets.QPushButton("LOGIN", self.LogGroupBox)
        self.LoginButton.setFixedSize(160, 60)
        self.LoginButton.setStyleSheet('font-size: 16px; font-weight: bold; color: green;')
        self.LogLayout.addWidget(self.LoginButton, 2, 1, QtCore.Qt.AlignCenter)

        self.LogGroupBox.setLayout(self.LogLayout)

        self.LogGroupBox.setVisible(isEnabled)

    def bookbrowsing_gui(self, isEnabled):
        # Book group box
        self.BookGroupBox = QtWidgets.QGroupBox("Book browsing", self)
        self.BookGroupBox.move(10, 60)
        self.BookGroupBox.setFixedSize(480, 220)

        self.mainWidget = QtWidgets.QTableView(self.BookGroupBox)
        self.mainWidget.move(5, 20)
        self.mainWidget.setFixedSize(250, 190)
        self.mainWidget.setSortingEnabled(True)
        self.list_process_data = []

        self.BookCommandDropBox = QtWidgets.QComboBox(self.BookGroupBox)
        self.BookCommandDropBox.addItems(['F_ID', 'F_Name', 'F_Type', 'F_Author'])
        self.BookCommandDropBox.move(260, 20)

        self.BookCommandText = QtWidgets.QLineEdit(self.BookGroupBox)
        self.BookCommandText.setFixedWidth(135)
        self.BookCommandText.setPlaceholderText("Enter string to search")
        self.BookCommandText.move(340, 20)

        self.SearchButton = QtWidgets.QPushButton("Search", self.BookGroupBox)
        self.SearchButton.move(380, 50)
        self.SearchButton.setFixedSize(95, 80)
        self.SearchButton.setStyleSheet('font-size: 16px')

        self.ViewButton = QtWidgets.QPushButton("View book", self.BookGroupBox)
        self.ViewButton.move(260, 50)
        self.ViewButton.setFixedSize(110, 35)

        self.DownloadButton = QtWidgets.QPushButton("Download book", self.BookGroupBox)
        self.DownloadButton.move(260, 95)
        self.DownloadButton.setFixedSize(110, 35)

        self.LogoutButton = QtWidgets.QPushButton("LOGOUT!", self.BookGroupBox)
        self.LogoutButton.move(260, 150)
        self.LogoutButton.setFixedSize(215, 60)
        self.LogoutButton.setStyleSheet('color: red; font-weight: bold; font-size: 20px;')

        self.BookGroupBox.setVisible(isEnabled)

    @QtCore.Slot()
    def add_click_behavior(self, obj, func):
        obj.clicked.connect(func)

    def change_GUI_status(self, StatusCode):
        if StatusCode == self.StatusCode.CONNECTING:
            ConnectingString = ['Connecting', 'Connecting.', 'Connecting..', 'Connecting...']
            text = self.ConnectButton.text()
            index = 3
            if (text != 'Connect!'):
                index = ConnectingString.index(text)
            index = (index + 1) % 4
            self.ConnectButton.setText(ConnectingString[index])

        if StatusCode == self.StatusCode.CONNECTED:
            self.ConnectButton.setText('Disconnect!')
            self.ConnectStatusBox.setText('CONNECTED!')
            self.ConnectStatusBox.setStyleSheet("border: 1.5px solid black; font-weight: bold; color: green;")

        if StatusCode == self.StatusCode.DISCONNECTED:
            self.ConnectButton.setText('Connect!')
            self.ConnectStatusBox.setText('DISCONNECTED!')
            self.ConnectStatusBox.setStyleSheet("border: 1.5px solid black; font-weight: bold; color: red;")

        if StatusCode == self.StatusCode.TIMEOUT:
            self.ConnectButton.setText('Connect!')
            self.ConnectStatusBox.setText('TIMED OUT!')
            self.ConnectStatusBox.setStyleSheet("border: 1.5px solid black; font-weight: bold; color: brown;")

        if StatusCode == self.StatusCode.LOGGED_IN:
            self.login_gui(False)
            self.bookbrowsing_gui(True)

        if StatusCode == self.StatusCode.LOGGED_OUT:
            self.login_gui(True)
            self.bookbrowsing_gui(False)

    def showError(self, error='NO CONNECTIONS', message='Please connect to server first'):
        msg = QtWidgets.QMessageBox()
        msg.setFixedWidth(200)
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText(error)
        msg.setInformativeText(message)
        msg.setWindowTitle(error)
        return msg

    class StatusCode(Enum):
        CONNECTED = auto(),
        DISCONNECTED = auto(),
        CONNECTING = auto(),
        TIMEOUT = auto(),
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

    window.login_gui(True)

    sys.exit(app.exec_())
