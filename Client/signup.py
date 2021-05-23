import socket
import sys
from PySide6 import QtCore, QtWidgets, QtGui
import logging
import json


class SignUpDialog(QtWidgets.QDialog):
    def __init__(self, sock):
        super().__init__()
        self.setWindowTitle('Sign up')
        self.sock = sock
        self.resize(300, 80)

        self.label_username = QtWidgets.QLabel("Username", self)
        self.username_textbox = QtWidgets.QLineEdit(self)
        self.username_regex = QtCore.QRegularExpression("[A-Za-z0-9._]+")
        self.username_validator = QtGui.QRegularExpressionValidator(self.username_regex)
        self.username_textbox.setValidator(self.username_validator)
        self.username_textbox.setFixedWidth(120)
        self.label_username.move(10, 10)
        self.username_textbox.move(85, 10)

        self.label_password = QtWidgets.QLabel("Password", self)
        self.password_textbox = QtWidgets.QLineEdit(self)
        self.password_regex = QtCore.QRegularExpression("[^-\s]+")
        self.password_validator = QtGui.QRegularExpressionValidator(self.password_regex)
        self.password_textbox.setValidator(self.password_validator)
        self.password_textbox.setFixedWidth(120)
        self.password_textbox.setEchoMode(QtWidgets.QLineEdit.Password)
        self.label_password.move(10, 40)
        self.password_textbox.move(85, 40)

        self.SignUpButton = QtWidgets.QPushButton('Sign up!', self)
        self.SignUpButton.setFixedSize(60, 53)
        self.SignUpButton.move(220, 10)

        self.SignUpButton.clicked.connect(self.sent_signup)

    def sent_signup(self):
        # remember to check username and password condition before sent register request
        username = self.username_textbox.text()
        password = self.password_textbox.text()
        if len(username) < 6 or len(password) < 4:
            message_box = QtWidgets.QMessageBox(self)
            message_box.setIcon(QtWidgets.QMessageBox.Information)
            message_box.setText('Username length must >= 6 and password length must >= 4')
            message_box.setWindowTitle('Error')
            message_box.exec_()
            return
        #string_sent = 'signup-' + username + '-' + password
        message = {'request': 'signup', 'username': username, 'password': password}
        self.sock.sendall(json.dumps(message).encode('utf-8'))
        recv_message = self.sock.recv(1024)
        recv_message = json.loads(recv_message.decode('utf8'))
        #recv_data = '02-ok'.encode('utf-8')
        if recv_message['request'] == 'signup' and recv_message['status'] == 'ok':
            message_box = QtWidgets.QMessageBox(self)
            message_box.setIcon(QtWidgets.QMessageBox.Information)
            message_box.setText('Successfully created account')
            message_box.setWindowTitle('Successful')
            message_box.exec_()
            self.close()
        else:
            message_box = QtWidgets.QMessageBox(self)
            message_box.setIcon(QtWidgets.QMessageBox.Information)
            message_box.setText('Username/password already existed')
            message_box.setWindowTitle('Error')
            message_box.exec_()


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = SignUpDialog(0)
    window.show()
    sys.exit(app.exec_())
