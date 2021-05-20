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


def click_connect_button(window):
    if (client_connection.connect_status == client_connection.ConnectStatusCode.DISCONNECTED
            or client_connection.connect_status == client_connection.ConnectStatusCode.TIMEOUT):

        host_str = str(window.IP_textbox.text())
        port_str = window.port_textbox.text()
        pos = 0
        if window.port_validator.validate(port_str, pos)[0] != window.port_validator.Acceptable:
            error_messagebox = window.show_error('Invalid Address', 'Invalid Port')
            error_messagebox.exec_()
            return -1
        port_str = int(port_str)
        # Try to connect to server for the first time, after DISCONNECTED or timeout seasion
        # turn status to connecting
        client_connection.connect_status = client_connection.ConnectStatusCode.CONNECTING
        window.change_GUI_status(window.ConnectStatusCode.CONNECTING)
        # try to connect to host
        connection_thread = threading.Thread(target=client_connection.start_connection, args=(host_str, port_str))
        connection_thread.start()

        # start timer - update GUI and send sample data to server (PING)
        window.timer_update_GUI.start(1000)

    elif (client_connection.connect_status == client_connection.ConnectStatusCode.CONNECTED):
        # Users choose to close connection
        client_connection.stop_connection()
        window.change_GUI_status(window.ConnectStatusCode.DISCONNECTED)
        # stop the timer
        window.timer_update_GUI.stop()


def click_signup_button(window):
    if client_connection.connect_status != client_connection.ConnectStatusCode.CONNECTED:
        # show error msg
        error_messagebox = window.show_error()
        error_messagebox.exec_()
        return -1

    signup_dialog = signup.SignUpDialog(client_connection.mainsock)
    subthread = threading.Thread(target=signup_dialog.exec_(), args=())
    subthread.start()


def click_login_button(window):
    if client_connection.connect_status != client_connection.ConnectStatusCode.CONNECTED:
        # show error msg
        error_messagebox = window.show_error()
        error_messagebox.exec_()
        return -1

    username = window.username_textbox.text()
    password = window.password_textbox.text()
    if (len(username) < 6) or (len(password) < 4):
        err_diag = QtWidgets.QMessageBox(window)
        err_diag.setFixedWidth(200)
        err_diag.setIcon(QtWidgets.QMessageBox.Information)
        err_diag.setText('Username must be longer than 5 characters\nPassword must be longer than 3 charaters \
                    \nRe-enter information to continue')
        err_diag.setWindowTitle('Username/Password error')
        err_diag.exec()
    else:
        #string_sent = 'login-' + window.username_textbox.text() + '-' + window.password_textbox.text()
        message_to_send = {'request': 'login', 'username': username, 'password': password}
        client_connection.send_message(message_to_send)

        recv_message = client_connection.mainsock.recv(1024)
        recv_message = json.loads(recv_message.decode('utf8'))
        if recv_message['request'] == 'login' and recv_message['status'] != 'ok':
            message_box = QtWidgets.QMessageBox(window)
            message_box.setText('Incorrect username or password')
            message_box.setWindowTitle('Error')
            message_box.exec_()
        else:
            client_connection.login_status = client_connection.LoginStatusCode.LOGGED_IN
            window.book_info_textbox.clear()
            window.main_widget.model().deleteLater()


def click_search_button(window):
    if client_connection.connect_status != client_connection.ConnectStatusCode.CONNECTED:
        # show error message
        error_messagebox = window.show_error()
        error_messagebox.exec_()
        return -1

    value = window.book_info_textbox.text()
    search_type = window.book_combobox.currentText()
    if len(value) == 0:
        message_box = QtWidgets.QMessageBox(window)
        message_box.setText('No value to search')
        message_box.exec_()
        return
    #string_sent = 'search-' + searchtype[2:] + '-' + value
    message_to_send = {'request': 'search', 'type': search_type[2:], 'value': value}
    client_connection.send_message(message_to_send)

    recv_message = ''
    data = client_connection.mainsock.recv(1024).decode('utf-8')
    while data and data[-4:] != '////':
        #logging.debug('data is {}'.format(data))
        recv_message = recv_message + str(data)
        data = client_connection.mainsock.recv(1024).decode('utf-8')
    recv_message = recv_message + str(data[:-4])
    recv_message = json.loads(recv_message)
    logging.debug('book receive: {}'.format(recv_message))

    if recv_message['status'] != 'ok':
        message_box = QtWidgets.QMessageBox(window)
        message_box.setText('No books available')
        message_box.exec_()
    else:
        book_dict = recv_message['books']
        book_list = window.list_book_to_table(book_dict)


def click_view_button(window):
    index = window.main_widget.selectedIndexes()
    if not index:
        logging.debug('No book selected')
        return
    row = index[0].row()
    book_info = '-'.join(window.main_widget.model().index(row, 0).data())

    #string_sent = 'view-' + info
    message_to_send = {'request': 'view', 'info': book_info}
    client_connection.send_message(message_to_send)

    recv_message = ''
    data = client_connection.mainsock.recv(1024)
    while data and data[-4:] != b'////':
        # logging.debug('data is {}'.format(data))
        recv_message = recv_message + data.decode('utf-8')
        data = client_connection.mainsock.recv(1024)

    recv_message = recv_message + data.decode('utf-8')[:-4]
    recv_message = json.loads(recv_message)
    if recv_message['status'] != 'ok':
        logging.debug('Cannot locate this book')
        return

    book_content = recv_message['book']

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


def click_download_button(window):
    index = window.main_widget.selectedIndexes()
    if not index:
        logging.debug('No book selected')
        return
    row = index[0].row()
    book_info = '-'.join(window.main_widget.model().index(row, 0).data())

    message_to_send = {'request': 'down', 'info': book_info}
    client_connection.send_message(message_to_send)

    recv_message = ''
    data = client_connection.mainsock.recv(1024)
    while data and data[-4:] != b'////':
        # logging.debug('data is {}'.format(data))
        recv_message = recv_message + data.decode('utf-8')
        data = client_connection.mainsock.recv(1024)

    recv_message = recv_message + data.decode('utf-8')[:-4]
    logging.debug('message is {}'.format(recv_message))
    recv_message = json.loads(recv_message)
    logging.debug('message is {}'.format(recv_message))
    if recv_message['status'] != 'ok':
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
        stream.write(recv_message['book'])
        stream.close()


def click_logout_button(window):
    client_connection.login_status = client_connection.LoginStatusCode.LOGGED_OUT
    window.password_textbox.clear()
    message_to_send = {'request': 'logout'}
    client_connection.send_message(message_to_send)


def update_GUI(window):
    if (client_connection.connect_status == client_connection.ConnectStatusCode.CONNECTING):
        window.change_GUI_status(window.ConnectStatusCode.CONNECTING)
    elif (client_connection.connect_status == client_connection.ConnectStatusCode.TIMEOUT):
        window.change_GUI_status(window.ConnectStatusCode.TIMEOUT)
    elif (client_connection.connect_status == client_connection.ConnectStatusCode.DISCONNECTED):
        # In case lost connection from server, we make notification to user
        if (client_connection.lost_connection == True):
            client_connection.lost_connection = False
            server_address = str(client_connection.mainsock.getpeername()[0]) + ':' + str(client_connection.mainsock.getpeername()[1])
            error_messagebox = window.show_error('Lost connection', ' from server: ' + server_address)
            error_messagebox.exec_()
        window.change_GUI_status(window.ConnectStatusCode.DISCONNECTED)
    elif (client_connection.connect_status == client_connection.ConnectStatusCode.CONNECTED):               # in-connecting
        if (client_connection.login_status == client_connection.LoginStatusCode.LOGGED_IN):
            window.change_GUI_status(window.ConnectStatusCode.CONNECTED, window.LoginStatusCode.LOGGED_IN)
        else:
            window.change_GUI_status(window.ConnectStatusCode.CONNECTED, window.LoginStatusCode.LOGGED_OUT)
        # sent ping request after every 1000ms to check server's signal
        message_to_send = {'request': 'ping'}
        client_connection.send_message(message_to_send)


def on_quit():
    if client_connection.connect_status == client_connection.ConnectStatusCode.CONNECTING \
            or client_connection.connect_status == client_connection.ConnectStatusCode.CONNECTED:
        client_connection.stop_connection()
    app.exit()


def connect_GUI_feature(window):
    app.lastWindowClosed.connect(on_quit)
    window.timer_update_GUI.timeout.connect(lambda: update_GUI(window))
    window.add_click_behavior(window.connect_button, lambda: click_connect_button(window))
    window.add_click_behavior(window.signup_button, lambda: click_signup_button(window))
    window.add_click_behavior(window.login_button, lambda: click_login_button(window))
    window.add_click_behavior(window.search_button, lambda: click_search_button(window))
    window.add_click_behavior(window.view_button, lambda: click_view_button(window))
    window.add_click_behavior(window.download_button, lambda: click_download_button(window))
    window.add_click_behavior(window.logout_button, lambda: click_logout_button(window))


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    app.setQuitOnLastWindowClosed(False)
    window = client_gui.ClientWindow()
    window.show()

    connect_GUI_feature(window)
    sys.exit(app.exec_())
