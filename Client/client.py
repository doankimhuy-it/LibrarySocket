import sys
import threading
import logging
import client_gui
import client_connect

client_connection = client_connect.ClientConnect()


def click_connectbutton(window):
    if (client_connection.connect_status == client_connection.StatusCode.DISCONNECT
            or client_connection.connect_status == client_connection.StatusCode.TIMEOUT):

        host_str = str(window.IPTextBox.text())
        port_str = window.PortTextBox.text()
        pos = 0
        if window.PortValidator.validate(port_str, pos)[0] != window.PortValidator.Acceptable:
            errmsg = window.showError('Invalid Address', 'Invalid Port')
            errmsg.exec_()
            return -1
        port_str = int(port_str)
        # Try to connect to server for the first time, after disconnect or timeout seasion
        # turn status to connecting
        client_connection.connect_status = client_connection.StatusCode.CONNECTING
        window.change_GUI_status(window.StatusCode.CONNECTING)
        # try to connect to host
        connection_thread = threading.Thread(target=client_connection.start_connection, args=(host_str, port_str))
        connection_thread.start()

        # start timer - update GUI and send sample data to server (PING)
        window.timer_update_GUI.start(500)

    elif (client_connection.connect_status == client_connection.StatusCode.CONNECTED):
        # Users choose to close connection
        client_connection.stop_connection()
        window.change_GUI_status(window.StatusCode.DISCONNECT)
        # stop the timer
        window.timer_update_GUI.stop()


def update_GUI(window):
    if (client_connection.connect_status == client_connection.StatusCode.CONNECTING):
        window.change_GUI_status(window.StatusCode.CONNECTING)
    elif (client_connection.connect_status == client_connection.StatusCode.TIMEOUT):
        window.change_GUI_status(window.StatusCode.TIMEOUT)
    elif (client_connection.connect_status == client_connection.StatusCode.DISCONNECT):
        # In case lost connection from server, we make notification to user
        if (client_connection.lost_connection == True):
            client_connection.lost_connection = False
            server_address = str(client_connection.mainsock.getpeername()[0]) + ':' + str(client_connection.mainsock.getpeername()[1])
            errmsg = window.showError('Lost connection', ' from server: ' + server_address)
            errmsg.exec_()
        window.change_GUI_status(window.StatusCode.DISCONNECT)
    elif (client_connection.connect_status == client_connection.StatusCode.CONNECTED):               # in-connecting
        window.change_GUI_status(window.StatusCode.CONNECTED)
        # sent '00' after every 500ms to check server's signal
        client_connection.send_message('00')


def on_quit():
    if client_connection.connect_status == client_connection.StatusCode.CONNECTING \
            or client_connection.connect_status == client_connection.StatusCode.CONNECTED:
        client_connection.stop_connection()
    app.exit()


def connect_GUI_feature(window):
    app.lastWindowClosed.connect(on_quit)
    window.timer_update_GUI.timeout.connect(lambda: update_GUI(window))
    window.add_click_behavior(window.ConnectButton, lambda: click_connectbutton(window))


if __name__ == '__main__':
    app = client_gui.QtWidgets.QApplication([])
    app.setQuitOnLastWindowClosed(False)
    window = client_gui.ClientWindow()
    window.show()

    connect_GUI_feature(window)
    sys.exit(app.exec_())
