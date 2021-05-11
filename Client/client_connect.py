import socket
import sys
import time
import logging
from enum import Enum, auto
# for debugging
logging.basicConfig(level=logging.DEBUG)


class ClientConnect:
    def __init__(self):
        self.connect_status = self.StatusCode.DISCONNECT
        self.host = '0.0.0.0'
        self.port = 0
        self.mainsock = 0
        self.lost_connection = False

    def start_connection(self, host, port):
        self.host = host
        self.port = port
        self.mainsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.mainsock.connect((self.host, self.port))
        except (ConnectionRefusedError, TimeoutError) as e: 
            logging.debug('Cannot connect to host {}'.format(e))
            self.connect_status = self.StatusCode.TIMEOUT   # timeout-status
            return
        else:
            logging.debug('Connected to server {}'.format(self.mainsock.getpeername()))
            self.connect_status = self.StatusCode.CONNECTED
    
    def send_message(self, message):
        message = message.encode('utf-8')
        try:
            self.mainsock.sendall(message)
        except:  # ConnectionAbortedError and ConnectionResetError
            logging.debug('Lost connection from {}'.format(self.mainsock.getpeername()))
            self.connect_status = self.StatusCode.DISCONNECT
            self.lost_connect = True

    def stop_connection(self):
        logging.debug('Closed connection to {}'.format(self.mainsock.getpeername()))
        end_message = 'Close'
        self.send_message(end_message)
        self.connect_status = self.StatusCode.DISCONNECT

    class StatusCode(Enum):
        CONNECTED = auto(),
        DISCONNECT = auto(),
        CONNECTING = auto(),
        TIMEOUT = auto()


if __name__ == '__main__':
    HOST = '192.168.1.11'  # The server's hostname or IP address
    PORT = 65432        # The port used by the server
    client_connect = ClientConnect()
    client_connect.start_connection(HOST, PORT)
