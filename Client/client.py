import sys
import threading
import logging
from PySide6 import QtWidgets
import client_gui
import client_connect
import signup

client_connection = client_connect.ClientConnect()


def click_connect_button(window):
    if (client_connection.connect_status == client_connection.ConnectStatusCode.DISCONNECTED
            or client_connection.connect_status == client_connection.ConnectStatusCode.TIMEOUT):

        host_str = str(window.IP_textbox.text())
        port_str = window.port_textbox.text()
        pos = 0
        if window.port_validator.validate(port_str, pos)[0] != window.port_validator.Acceptable:
            window.MessageError('Invalid Address Invalid Port')
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
        client_connection.logout_request()
        client_connection.stop_connection()
        window.username_textbox.clear()
        window.password_textbox.clear()
        window.change_GUI_status(window.ConnectStatusCode.DISCONNECTED)
        # stop the timer
        window.timer_update_GUI.stop()


def click_signup_button(window):
    signup_dialog = signup.SignUpDialog(client_connection.mainsock)
    subthread = threading.Thread(target=signup_dialog.exec_(), args=())
    subthread.start()


def click_login_button(window):
    username, password = window.get_username_password()
    if username:
        if client_connection.login_request(username, password) == True:
            window.book_info_textbox.clear()
            if window.main_widget.model() != None:
                window.main_widget.model().deleteLater()
        else:
            window.MessageError('Incorrect username or password')


def click_search_button(window):

    search_type, value = window.value_to_search()
    if value == None:
        return

    server_response = client_connection.search_request(search_type, value)
    if server_response['code'] == 'ok':
        window.list_book_to_table(server_response['data'])
    else:
        window.MessageError('No books available')


def click_view_button(window):

    ID = window.ID_selected_book()
    if not ID:
        return

    book_content = client_connection.view_request(ID)
    if not book_content:
        window.MessageError('Book deleted on server!')
    else:
        window.show_book_content(book_content)


def click_download_button(window):

    ID = window.ID_selected_book()
    if not ID:
        return

    book_content = client_connection.download_request(ID)
    if not book_content:
        logging.debug('Book deleted on server!')
        window.MessageError('Book deleted on server!')
        return

    file_filter = 'Text Document (*.txt)'
    file_prompt = QtWidgets.QFileDialog.getSaveFileName(
        parent=window,
        caption='Save as',
        filter=file_filter)

    filename = file_prompt[0]
    if filename:
        stream = open(filename, 'wt')
        stream.write(book_content)
        stream.close()


def click_logout_button(window):
    window.password_textbox.clear()
    client_connection.logout_request()


def update_GUI(window):
    connect_status = client_connection.connect_status
    if (connect_status == client_connection.ConnectStatusCode.CONNECTING):
        window.change_GUI_status(window.ConnectStatusCode.CONNECTING)

    if (connect_status == client_connection.ConnectStatusCode.TIMEOUT):
        window.change_GUI_status(window.ConnectStatusCode.TIMEOUT)

    if (connect_status == client_connection.ConnectStatusCode.DISCONNECTED):
        # In case lost connection from server, we make notification to user
        if (client_connection.lost_connection == True):
            client_connection.lost_connection = False
            server_address = str(client_connection.mainsock.getpeername()[0]) + ':' + str(client_connection.mainsock.getpeername()[1])
            err = 'Lost connection from server: ' + server_address
            window.MessageError(err)

        window.change_GUI_status(window.ConnectStatusCode.DISCONNECTED)

    if (connect_status == client_connection.ConnectStatusCode.CONNECTED):               # in-connecting
        if (client_connection.login_status == client_connection.LoginStatusCode.LOGGED_IN):
            window.change_GUI_status(window.ConnectStatusCode.CONNECTED, window.LoginStatusCode.LOGGED_IN)
        else:
            window.change_GUI_status(window.ConnectStatusCode.CONNECTED, window.LoginStatusCode.LOGGED_OUT)
        # sent ping request after every 1000ms to check server's signal
        client_connection.send_ping()


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
