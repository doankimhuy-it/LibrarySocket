import socket
import sys
from PySide6 import QtCore, QtWidgets, QtGui
import logging

class SignUpDialog(QtWidgets.QDialog):
    def __init__(self, sock):
        super().__init__()
        self.setWindowTitle('Sign up')
        self.sock = sock     
        self.resize(300, 80)

        self.label_username = QtWidgets.QLabel("Username", self)
        self.UsernameBox = QtWidgets.QLineEdit(self)
        self.UsernameRegex = QtCore.QRegularExpression("[A-Za-z0-9._]+")
        self.UsernameValidator = QtGui.QRegularExpressionValidator(self.UsernameRegex)
        self.UsernameBox.setValidator(self.UsernameValidator)
        self.UsernameBox.setFixedWidth(100)
        self.label_username.move(10, 10)
        self.UsernameBox.move(100, 10)

        self.label_password = QtWidgets.QLabel("Password", self)
        self.PasswordBox = QtWidgets.QLineEdit(self)
        self.PasswordRegex = QtCore.QRegularExpression("[^-\s]+")
        self.PasswordValidator = QtGui.QRegularExpressionValidator(self.PasswordRegex)
        self.PasswordBox.setValidator(self.PasswordValidator)
        self.PasswordBox.setFixedWidth(100)
        self.label_password.move(10, 40)
        self.PasswordBox.move(100, 40)

        self.SignUpButton = QtWidgets.QPushButton('Sign up!', self)
        self.SignUpButton.setFixedSize(60, 60)
        self.SignUpButton.move(220, 10)

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = SignUpDialog(0)
    #print(window.list_process_data)
    window.show()
    sys.exit(app.exec_())