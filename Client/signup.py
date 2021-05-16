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

        self.SignUpButton.clicked.connect(self.sent_signup)

    def sent_signup(self):
        # remember to check username and password condition before sent register request
        username = self.UsernameBox.text()
        password = self.PasswordBox.text()
        if len(username) < 6 or len(password) < 6:
            MessBox = QtWidgets.QMessageBox(self)
            MessBox.setText('Username and password length must >= 6')
            MessBox.exec_()
            return
        string_sent = 'signup-' + username + '-' + password 
        self.sock.sendall(string_sent.encode('utf-8'))
        recv_data = self.sock.recv(1024)
        #recv_data = '02-ok'.encode('utf-8')
        if recv_data.decode('utf-8') == 'signup-ok':
            MessBox = QtWidgets.QMessageBox(self)
            MessBox.setText('Successful')
            MessBox.exec_()
            self.close()
        else:
            MessBox = QtWidgets.QMessageBox(self)
            MessBox.setText('Username already existed')
            MessBox.exec_()


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = SignUpDialog(0)
    #print(window.list_process_data)
    window.show()
    sys.exit(app.exec_())