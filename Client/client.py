import sys
import threading
import logging
from PySide6 import QtCore, QtWidgets, QtGui
import client_gui
import client_connect
import signup
import io

client_connection = client_connect.ClientConnect()


def click_connectbutton(window):
    if (client_connection.connect_status == client_connection.StatusCode.DISCONNECTED
            or client_connection.connect_status == client_connection.StatusCode.TIMEOUT):

        host_str = str(window.IPTextBox.text())
        port_str = window.PortTextBox.text()
        pos = 0
        if window.PortValidator.validate(port_str, pos)[0] != window.PortValidator.Acceptable:
            errmsg = window.showError('Invalid Address', 'Invalid Port')
            errmsg.exec_()
            return -1
        port_str = int(port_str)
        # Try to connect to server for the first time, after DISCONNECTED or timeout seasion
        # turn status to connecting
        client_connection.connect_status = client_connection.StatusCode.CONNECTING
        window.change_GUI_status(window.StatusCode.CONNECTING)
        # try to connect to host
        connection_thread = threading.Thread(target=client_connection.start_connection, args=(host_str, port_str))
        connection_thread.start()

        # start timer - update GUI and send sample data to server (PING)
        window.timer_update_GUI.start(1000)

    elif (client_connection.connect_status == client_connection.StatusCode.CONNECTED):
        # Users choose to close connection
        client_connection.stop_connection()
        window.change_GUI_status(window.StatusCode.DISCONNECTED)
        # stop the timer
        window.timer_update_GUI.stop()


def click_signupbutton(window):
    if client_connection.connect_status != client_connection.StatusCode.CONNECTED:
        # show error msg
        errmsg = window.showError()
        errmsg.exec_()
        return -1

    signup_dialog = signup.SignUpDialog(client_connection.mainsock)
    subthread = threading.Thread(target=signup_dialog.exec_(), args=())
    subthread.start()


def click_loginbutton(window):
    if client_connection.connect_status != client_connection.StatusCode.CONNECTED:
        # show error msg
        errmsg = window.showError()
        errmsg.exec_()
        return -1

    string_sent = 'login-' + window.UsernameBox.text() + '-' + window.PasswordBox.text()
    client_connection.send_message(string_sent)

    recv_msg = client_connection.mainsock.recv(1024).decode('utf8')
    if recv_msg == 'login-error':
        MessBox = QtWidgets.QMessageBox(window)
        MessBox.setText('Incorrect username or password')
        MessBox.exec_()
    else:
        client_connection.login_status = client_connection.StatusCode.LOGGED_IN


def click_searchbutton(window):
    if client_connection.connect_status != client_connection.StatusCode.CONNECTED:
        # show error msg
        errmsg = window.showError()
        errmsg.exec_()
        return -1

    string_sent =  'search-' + window.BookCommandDropBox.currentText()[2:] + '-' \
        + window.BookCommandText.text()
    client_connection.send_message(string_sent)

    recv_msg = client_connection.mainsock.recv(1024).decode('utf8')
    if recv_msg == 'search-ok':
        client_connection.book_status.BOOK_AVAILABLE


def click_viewbutton(window):
    string_sent = 'view-' + window.BookCommandDropBox.currentText()[2:] + '-' \
        + window.BookCommandText.text()
    client_connection.send_message(string_sent)

    data_stream = io.BytesIO()
    data = client_connection.mainsock.recv(1024)
    while data and data[-4:] != b'////':
        # logging.debug('data is {}'.format(data))
        data_stream.write(data)
        data = client_connection.mainsock.recv(1024)

    data_stream.write(data[:-4])

    view_diag = QtWidgets.QDialog(window)
    view_diag.setWindowTitle('Book content')
    view_diag.setFixedSize(200, 200)

    book_content = QtWidgets.QTextEdit(view_diag)
    book_content.move(20, 20)
    book_content.setFixedSize(180, 180)

    book_content.setText(str(data_stream.getvalue()))


def click_downloadbutton(window):
    string_sent = 'down-' + window.BookCommandDropBox.currentText()[2:] + '-' \
        + window.BookCommandText.text()
    client_connection.send_message(string_sent)

    data_stream = io.BytesIO()
    data = client_connection.mainsock.recv(1024)
    while data and data[-4:] != b'////':
        # logging.debug('data is {}'.format(data))
        data_stream.write(data)
        data = client_connection.mainsock.recv(1024)

    data_stream.write(data[:-4])

    file_filter = 'Text Document (*.txt)'
    response = QtWidgets.QFileDialog.getSaveFileName(
        parent=window,
        caption='Save as',
        filter=file_filter,
    )
    print(response[0])

    filename = response[0]
    if filename:
        stream = open(filename, 'wb')
        stream.write(data_stream.getvalue())
        stream.close()


def click_logoutbutton(window):
    client_connection.login_status = client_connection.StatusCode.LOGGED_OUT


def update_GUI(window):
    if (client_connection.connect_status == client_connection.StatusCode.CONNECTING):
        window.change_GUI_status(window.StatusCode.CONNECTING)
    elif (client_connection.connect_status == client_connection.StatusCode.TIMEOUT):
        window.change_GUI_status(window.StatusCode.TIMEOUT)
    elif (client_connection.connect_status == client_connection.StatusCode.DISCONNECTED):
        # In case lost connection from server, we make notification to user
        if (client_connection.lost_connection == True):
            client_connection.lost_connection = False
            server_address = str(client_connection.mainsock.getpeername()[0]) + ':' + str(client_connection.mainsock.getpeername()[1])
            errmsg = window.showError('Lost connection', ' from server: ' + server_address)
            errmsg.exec_()
        window.change_GUI_status(window.StatusCode.DISCONNECTED)
    elif (client_connection.connect_status == client_connection.StatusCode.CONNECTED):               # in-connecting
        window.change_GUI_status(window.StatusCode.CONNECTED)
        # sent '00' after every 1000ms to check server's signal
        client_connection.send_message('00')

    if (client_connection.login_status == client_connection.StatusCode.LOGGED_IN):
        window.change_GUI_status(window.StatusCode.LOGGED_IN)
    elif (client_connection.login_status == client_connection.StatusCode.LOGGED_OUT):
        window.change_GUI_status(window.StatusCode.LOGGED_OUT)

    if (client_connection.book_status == client_connection.StatusCode.BOOK_AVAILABLE):
        window.change_GUI_status(window.StatusCode.BOOK_AVAILABLE)
    elif (client_connection.login_status == client_connection.StatusCode.BOOK_UNAVAILABLE):
        window.change_GUI_status(window.StatusCode.BOOK_UNAVAILABLE)


def on_quit():
    if client_connection.connect_status == client_connection.StatusCode.CONNECTING \
            or client_connection.connect_status == client_connection.StatusCode.CONNECTED:
        client_connection.stop_connection()
    app.exit()


def connect_GUI_feature(window):
    app.lastWindowClosed.connect(on_quit)
    window.timer_update_GUI.timeout.connect(lambda: update_GUI(window))
    window.add_click_behavior(window.ConnectButton, lambda: click_connectbutton(window))
    window.add_click_behavior(window.SignupButton, lambda: click_signupbutton(window))
    window.add_click_behavior(window.LoginButton, lambda: click_loginbutton(window))
    window.add_click_behavior(window.SearchButton, lambda: click_searchbutton(window))
    window.add_click_behavior(window.ViewButton, lambda: click_viewbutton(window))
    window.add_click_behavior(window.DownloadButton, lambda: click_downloadbutton(window))
    window.add_click_behavior(window.LogoutButton, lambda: click_logoutbutton(window))


if __name__ == '__main__':
    app = client_gui.QtWidgets.QApplication([])
    app.setQuitOnLastWindowClosed(False)
    window = client_gui.ClientWindow()
    window.show()

    connect_GUI_feature(window)
    sys.exit(app.exec_())
