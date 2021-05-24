import json
import socket
import logging
from enum import Enum, auto
# for debugging
logging.basicConfig(level=logging.DEBUG)


class ClientConnect:
    def __init__(self):
        self.connect_status = self.ConnectStatusCode.DISCONNECTED
        self.login_status = self.LoginStatusCode.LOGGED_OUT
        self.host = '0.0.0.0'
        self.port = 0
        self.mainsock = 0
        self.lost_connection = False

    def search_request(self, search_type, value):
        message_to_send = {'request': 'search', 'type': search_type, 'value': value}
        self.send_message(message_to_send)

        recv_message = ''
        data = self.mainsock.recv(1024).decode('utf-8')
        while data and data[-4:] != '////':
            recv_message = recv_message + str(data)
            data = self.mainsock.recv(1024).decode('utf-8')
        recv_message = recv_message + str(data[:-4])
        recv_message = json.loads(recv_message)
        logging.debug('Books received: {}'.format(recv_message))

        if recv_message['request'] == 'search' and recv_message['status'] == 'ok':
            book_dict = recv_message['books']
            return {'code': 'ok', 'data': book_dict}
        else:
            return {'code': 'err',}
            
    def view_request(self, ID):
        message_to_send = {'request': 'view', 'ID': ID}
        self.send_message(message_to_send)

        recv_message = ''
        data = self.mainsock.recv(1024)
        while data and data[-4:] != b'////':
            # logging.debug('data is {}'.format(data))
            recv_message = recv_message + data.decode('utf-8')
            data = self.mainsock.recv(1024)

        recv_message = recv_message + data.decode('utf-8')[:-4]
        recv_message = json.loads(recv_message)
        if recv_message['status'] != 'ok':
            logging.debug('Cannot locate this book')
            return None
        book_content = recv_message['book']
        return book_content

    def download_request(self, ID):
        message_to_send = {'request': 'down', 'ID': ID}
        self.send_message(message_to_send)

        recv_message = ''
        data = self.mainsock.recv(1024)
        while data and data[-4:] != b'////':
            # logging.debug('data is {}'.format(data))
            recv_message = recv_message + data.decode('utf-8')
            data = self.mainsock.recv(1024)

        recv_message = recv_message + data.decode('utf-8')[:-4]
        recv_message = json.loads(recv_message)
        if recv_message['status'] != 'ok':
            return None
        else:
            return recv_message['book']

    def logout_request(self):
        self.login_status = self.LoginStatusCode.LOGGED_OUT
        message_to_send = {'request': 'logout'}
        self.send_message(message_to_send)

    def login_request(self, username, password):
        message_to_send = {'request': 'login', 'username': username, 'password': password}
        self.send_message(message_to_send)
        recv_message = self.mainsock.recv(1024)
        recv_message = json.loads(recv_message.decode('utf8'))
        if recv_message['request'] == 'login' and recv_message['status'] == 'ok':
            self.login_status = self.LoginStatusCode.LOGGED_IN
            return True
        else:
            return False
            
    def start_connection(self, host, port):
        self.host = host
        self.port = port
        self.mainsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.mainsock.connect((self.host, self.port))
        except (ConnectionRefusedError, TimeoutError) as e:
            logging.debug('Cannot connect to host {}'.format(e))
            self.connect_status = self.ConnectStatusCode.TIMEOUT   # timeout-status
            return
        else:
            logging.debug('Connected to server {}'.format(self.mainsock.getpeername()))
            self.connect_status = self.ConnectStatusCode.CONNECTED

    def send_ping(self):
        ping_message = {'request': 'ping'}
        self.send_message(ping_message)

    def send_message(self, message):
        message = json.dumps(message).encode('utf-8')
        try:
            self.mainsock.sendall(message)
        except:  # ConnectionAbortedError and ConnectionResetError
            logging.debug('Lost connection from {}'.format(self.mainsock.getpeername()))
            self.connect_status = self.ConnectStatusCode.DISCONNECTED
            self.lost_connection = True

    def stop_connection(self):
        logging.debug('Closed connection to {}'.format(self.mainsock.getpeername()))
        end_message = {'request': 'close_connection'}
        self.send_message(end_message)
        self.connect_status = self.ConnectStatusCode.DISCONNECTED
        self.login_status = self.LoginStatusCode.LOGGED_OUT


    class ConnectStatusCode(Enum):
        CONNECTED = auto(),
        DISCONNECTED = auto(),
        CONNECTING = auto(),
        TIMEOUT = auto()

    class LoginStatusCode(Enum):
        LOGGED_IN = auto(),
        LOGGED_OUT = auto()


if __name__ == '__main__':
    HOST = '192.168.1.11'  # The server's hostname or IP address
    PORT = 65432        # The port used by the server
    client_connect = ClientConnect()
    client_connect.start_connection(HOST, PORT)
