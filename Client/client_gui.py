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
        self.ConnectStatusBox.setStyleSheet("QLabel { border: 1.5px solid black;font-weight: bold; color : red; }")

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
        self.UsernameBox.setFixedWidth(300)
        self.LogLayout.addWidget(self.label_username, 0, 0)
        self.LogLayout.addWidget(self.UsernameBox, 0, 1)

        # Password box
        self.label_password = QtWidgets.QLabel("Password", self.LogGroupBox)
        self.PasswordBox = QtWidgets.QLineEdit(self.LogGroupBox)
        self.PasswordRegex = QtCore.QRegularExpression("[^-\s]+")
        self.PasswordValidator = QtGui.QRegularExpressionValidator(self.PasswordRegex)
        self.PasswordBox.setValidator(self.PasswordValidator)
        self.PasswordBox.setFixedWidth(300)
        self.LogLayout.addWidget(self.label_password, 1, 0)
        self.LogLayout.addWidget(self.PasswordBox, 1, 1)

        # Button layout to store two
        self.ButtonLayout = QtWidgets.QGridLayout(self.LogGroupBox)
        self.LogLayout.addLayout(self.ButtonLayout, 2, 1)

        # Sign-up button
        self.SignupButton = QtWidgets.QPushButton("Sign up", self.LogGroupBox)
        self.SignupButton.setFixedSize(80, 40)
        self.ButtonLayout.addWidget(self.SignupButton, 0, 0)
        # Login button
        self.LoginButton = QtWidgets.QPushButton("Login", self.LogGroupBox)
        self.LoginButton.setFixedSize(80, 40)
        self.ButtonLayout.addWidget(self.LoginButton, 0, 1)

        self.LogGroupBox.setLayout(self.LogLayout)

        self.LogGroupBox.setVisible(True)

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
            self.ConnectStatusBox.setStyleSheet("QLabel { border: 1.5px solid black;font-weight: bold; color : green; }")

        if StatusCode == self.StatusCode.DISCONNECTED:
            self.ConnectButton.setText('Connect!')
            self.ConnectStatusBox.setText('DISCONNECTED!')
            self.ConnectStatusBox.setStyleSheet("QLabel { border: 1.5px solid black;font-weight: bold; color : red; }")

        if StatusCode == self.StatusCode.TIMEOUT:
            self.ConnectButton.setText('Connect!')
            self.ConnectStatusBox.setText('TIMED OUT!')
            self.ConnectStatusBox.setStyleSheet("QLabel { border: 1.5px solid black;font-weight: bold; color : brown ; }")

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
        LOGGED_IN = auto()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    window = ClientWindow()
    window.show()

    sys.exit(app.exec_())
