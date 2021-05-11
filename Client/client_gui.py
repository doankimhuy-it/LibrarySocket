# Python GUI
import sys
from PySide6 import QtCore, QtWidgets, QtGui
import logging
from enum import Enum, auto

logging.basicConfig(level=logging.DEBUG)


class ClientWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.timer_update_GUI = QtCore.QTimer()

        # create windows title and its size
        self.setWindowTitle("Client")
        self.setFixedSize(500, 60)

        # IP box
        self.IPTextBox = QtWidgets.QLineEdit("127.0.0.1", self)
        self.IPTextBox.move(10, 20)
        self.IPTextBox.setFixedWidth(200)

        # Port box
        self.PortTextBox = QtWidgets.QLineEdit("65432", self)
        self.validator = QtGui.QIntValidator(0, 65535, self)
        self.PortTextBox.setValidator(self.validator)
        self.PortTextBox.move(self.IPTextBox.geometry().x() + self.IPTextBox.width() + 5, 20)
        self.PortTextBox.setFixedWidth(50)

        # Connect button
        self.ConnectButton = QtWidgets.QPushButton("Connect!", self)
        self.ConnectButton.move(self.PortTextBox.geometry().x() + self.PortTextBox.width() + 5, 20)
        buttonwidth = -10 + self.ConnectButton.geometry().x() + self.ConnectButton.width()

        # Connect status
        self.ConnectStatusBox = QtWidgets.QLabel("DISCONNECTED!", self, alignment=QtCore.Qt.AlignCenter)
        self.ConnectStatusBox.move(10 + self.ConnectButton.geometry().x() + self.ConnectButton.width(), 20)
        self.ConnectStatusBox.setStyleSheet("QLabel { border: 1.5px solid black;font-weight: bold; color : red; }")


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
            self.ConnectStatus.setText('CONNECTED!')
            self.ConnectStatus.setStyleSheet("QLabel { border: 1.5px solid black;font-weight: bold; color : green; }")

        if StatusCode == self.StatusCode.DISCONNECT:
            self.ConnectButton.setText('Connect!')
            self.ConnectStatus.setText('DISCONNECTED!')
            self.ConnectStatus.setStyleSheet("QLabel { border: 1.5px solid black;font-weight: bold; color : red; }")

        if StatusCode == self.StatusCode.TIMEOUT:
            self.ConnectButton.setText('Connect!')
            self.ConnectStatus.setText('TIMED OUT!')
            self.ConnectStatus.setStyleSheet("QLabel { border: 1.5px solid black;font-weight: bold; color : brown ; }")

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
        DISCONNECT = auto(),
        CONNECTING = auto(),
        TIMEOUT = auto()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    window = ClientWindow()
    window.show()

    sys.exit(app.exec_())
