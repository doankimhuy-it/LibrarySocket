import sys
import threading
import logging
from PySide6 import QtCore, QtWidgets, QtGui
import client_gui
import client_connect
import signup
import io
import json

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


def conver_list2dict(dictbook):

    listbook = []
    for i in range(len(listbook)):
        p = dict(zip(keys, listbook[i]))
        dictbooks.update({i: p})
    return dictbooks


def click_searchbutton(window):
    if client_connection.connect_status != client_connection.StatusCode.CONNECTED:
        # show error msg
        errmsg = window.showError()
        errmsg.exec_()
        return -1

    value = window.BookCommandText.text()
    searchtype = window.BookCommandDropBox.currentText()
    if len(value) == 0:
        MessBox = QtWidgets.QMessageBox(window)
        MessBox.setText('No value to search')
        MessBox.exec_()
        return
    string_sent = 'search-' + searchtype[2:] + '-' \
        + value
    client_connection.send_message(string_sent)

    message = ''
    data = client_connection.mainsock.recv(1024).decode('utf-8')
    while data and data[-4:] != '////':
        #logging.debug('data is {}'.format(data))
        message = message + str(data)
        data = client_connection.mainsock.recv(1024).decode('utf-8')
    message = message + str(data[:-4])
    message = json.loads(message)
    logging.debug('book recieve: {}'.format(message))

    if message['response'] != 'ok':
        MessBox = QtWidgets.QMessageBox(window)
        MessBox.setText('No book')
        MessBox.exec_()
    else:
        dictbook = message['books']
        book_list = window.list_book_to_table(dictbook)


def click_viewbutton(window):
    index = window.mainWidget.selectedIndexes()
    if not index:
        logging.debug('No book selected')
        return
    row = index[0].row()
    info = '-'.join(window.mainWidget.model().index(row, 0).data())

    string_sent = 'view-' + info
    client_connection.send_message(string_sent)

    response = ''
    data = client_connection.mainsock.recv(1024)
    while data and data[-4:] != b'////':
        # logging.debug('data is {}'.format(data))
        response = response + data.decode('utf-8')
        data = client_connection.mainsock.recv(1024)

    response = response + data.decode('utf-8')[:-4]
    response = json.loads(response)
    if response['response'] != 'ok':
        logging.debug('Cannot locate this book')
        return

    book_content = response['book']

    view_diag = QtWidgets.QDialog(window)
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


def click_downloadbutton(window):
    index = window.mainWidget.selectedIndexes()
    if not index:
        logging.debug('No book selected')
        return
    row = index[0].row()
    info = '-'.join(window.mainWidget.model().index(row, 0).data())

    string_sent = 'down-' + info
    client_connection.send_message(string_sent)

    data_stream = io.BytesIO()
    response = ''
    data = client_connection.mainsock.recv(1024)
    while data and data[-4:] != b'////':
        # logging.debug('data is {}'.format(data))
        response = response + data.decode('utf-8')
        data = client_connection.mainsock.recv(1024)

    response = response + data.decode('utf-8')[:-4]
    logging.debug('response is {}'.format(response))
    response = json.loads(response)
    logging.debug('response is {}'.format(response))
    if response['response'] != 'ok':
        logging.debug('Cannot locate this book')
        return

    file_filter = 'Text Document (*.txt)'
    file_prompt = QtWidgets.QFileDialog.getSaveFileName(
        parent=window,
        caption='Save as',
        filter=file_filter)
    print(file_prompt[0])

    filename = file_prompt[0]
    if filename:
        stream = open(filename, 'wt')
        stream.write(response['book'])
        stream.close()


def click_logoutbutton(window):
    client_connection.login_status = client_connection.StatusCode.LOGGED_OUT
    client_connection.send_message('logout')


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
    app = QtWidgets.QApplication([])
    app.setQuitOnLastWindowClosed(False)
    window = client_gui.ClientWindow()
    window.show()

    connect_GUI_feature(window)
    sys.exit(app.exec_())
