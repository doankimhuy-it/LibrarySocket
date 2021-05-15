# Python GUI
import sys
from PySide6 import QtCore, QtWidgets, QtGui
import logging
from enum import Enum, auto
import re

logging.basicConfig(level=logging.DEBUG)


class ClientWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.timer_update_GUI = QtCore.QTimer()

        # create windows title and its size
        self.setWindowTitle("Client")
        self.setFixedSize(500, 200)

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

        # Login/Logout group box
        self.LogGroupBox = QtWidgets.QGroupBox("Login/Sign up", self)
        self.LogGroupBox.move(20, 60)
        self.LogGroupBox.setFixedSize(460, 130)

        self.LogLayout = QtWidgets.QGridLayout(self.LogGroupBox)

        # Username box
        self.label_username = QtWidgets.QLabel("Username", self.LogGroupBox)
        self.UsernameBox = QtWidgets.QLineEdit(self.LogGroupBox)
        self.UsernameRegex = QtCore.QRegularExpression("[A-Za-z0-9._]+")
        self.UsernameValidator = QtGui.QRegularExpressionValidator(self.UsernameRegex)
        self.UsernameBox.setValidator(self.UsernameValidator)
        self.UsernameBox.setFixedWidth(250)
        self.LogLayout.addWidget(self.label_username, 0, 0)
        self.LogLayout.addWidget(self.UsernameBox, 0, 1)

        # Password box
        self.label_password = QtWidgets.QLabel("Password", self.LogGroupBox)
        self.PasswordBox = QtWidgets.QLineEdit(self.LogGroupBox)
        self.PasswordRegex = QtCore.QRegularExpression("[^-\s]+")
        self.PasswordValidator = QtGui.QRegularExpressionValidator(self.PasswordRegex)
        self.PasswordBox.setValidator(self.PasswordValidator)
        self.PasswordBox.setFixedWidth(250)
        self.LogLayout.addWidget(self.label_password, 1, 0)
        self.LogLayout.addWidget(self.PasswordBox, 1, 1)

        # Sign-up button
        self.SignupButton = QtWidgets.QPushButton("No account?\nSign up", self.LogGroupBox)
        self.SignupButton.setFixedSize(80, 40)
        self.LogLayout.addWidget(self.SignupButton, 2, 0)

        # Login button
        self.LoginButton = QtWidgets.QPushButton("Login", self.LogGroupBox)
        self.LoginButton.setFixedSize(80, 40)
        self.LogLayout.addWidget(self.LoginButton, 2, 1, QtCore.Qt.AlignCenter)

        self.LogGroupBox.setLayout(self.LogLayout)

        self.LogGroupBox.setVisible(True)

        # Book group box
        self.BookGroupBox = QtWidgets.QGroupBox("Book browsing", self)
        self.BookGroupBox.move(20, 60)
        self.BookGroupBox.setFixedSize(460, 130)

        self.BookLayout = QtWidgets.QGridLayout(self.BookGroupBox)

        self.BookCommandDropBox = QtWidgets.QComboBox(self.BookGroupBox)
        self.BookCommandDropBox.addItems(['F_ID', 'F_Name', 'F_Type', 'F_Author'])

        self.BookCommandText = QtWidgets.QLineEdit(self.BookGroupBox)
        self.BookCommandText.setFixedWidth(170)
        self.BookCommandText.setPlaceholderText("Enter correct string to search")

        self.SearchButton = QtWidgets.QPushButton("SearchButton", self.BookGroupBox)

        self.BookStatus = QtWidgets.QLabel("BOOK STATUS", self, alignment=QtCore.Qt.AlignCenter)
        self.BookStatus.setStyleSheet("border: 1.5px solid black; font-weight: bold; color: black;")
        self.BookStatus.setFixedWidth(100)

        self.ViewButton = QtWidgets.QPushButton("View book", self.BookGroupBox)
        self.DownloadButton = QtWidgets.QPushButton("Download book", self.BookGroupBox)
        self.LogoutButton = QtWidgets.QPushButton("LOGOUT!", self.BookGroupBox)
        self.LogoutButton.setFixedHeight(60)
        self.LogoutButton.setStyleSheet('color: red; font-weight: bold; font-size: 20px;')

        self.BookLayout.addWidget(self.BookCommandDropBox, 0, 0)
        self.BookLayout.addWidget(self.BookCommandText, 0, 1)
        self.BookLayout.addWidget(self.SearchButton, 0, 2)
        self.BookLayout.addWidget(self.BookStatus, 0, 3)
        self.BookLayout.addWidget(self.ViewButton, 1, 0)
        self.BookLayout.addWidget(self.DownloadButton, 1, 1)
        self.BookLayout.addWidget(self.LogoutButton, 1, 2, 1, 2)

        self.BookGroupBox.setLayout(self.BookLayout)

        self.BookGroupBox.setVisible(False)

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
            self.LogGroupBox.setVisible(False)
            self.BookGroupBox.setVisible(True)

        if StatusCode == self.StatusCode.LOGGED_OUT:
            self.LogGroupBox.setVisible(True)
            self.BookGroupBox.setVisible(False)

        if StatusCode == self.StatusCode.BOOK_UNAVAILABLE:
            self.ViewButton.setVisible(False)
            self.DownloadButton.setVisible(False)
            self.BookStatus.setText('AVAILABLE')
            self.BookStatus.setStyleSheet("border: 1.5px solid black; font-weight: bold; color: green;")

        if StatusCode == self.StatusCode.BOOK_UNAVAILABLE:
            self.ViewButton.setVisible(True)
            self.DownloadButton.setVisible(True)
            self.BookStatus.setText('UNAVAILABLE')
            self.BookStatus.setStyleSheet("border: 1.5px solid black; font-weight: bold; color: red;")

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
        LOGGED_OUT = auto(),
        BOOK_UNAVAILABLE = auto(),
        BOOK_AVAILABLE = auto()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    window = ClientWindow()
    window.show()

    sys.exit(app.exec_())
