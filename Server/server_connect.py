import selectors    # working with multi-clients
import socket       # socket
import logging
import SQL_Query
import json
logging.basicConfig(level=logging.DEBUG)


class ServerConnection:
    def __init__(self, host, port):
        self.connect_status = 0
        self.sel = selectors.DefaultSelector()           # Monitor will hand all of connections
        self.host = host
        self.port = port
        self.SQL = SQL_Query.SQL_CONNECT('localhost', 'LIBRARYSOCKET', 'sa', '1234')
        self.is_loggedin = False

    def start_listen(self):
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # USE TCP/IP Connection
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sel.register(self.server_sock, selectors.EVENT_READ, data=None)
        self.server_sock.bind((self.host, self.port))
        # accept 10 connections
        self.server_sock.listen(10)
        self.connect_status = 1  # set to start listening flag, 1 is one socket (server_sock)

        logging.debug('Listening on {} : {}'.format(self.host, self.port))
        while self.connect_status:
            try:
                event = self.sel.select(timeout=0)  # timeout = 0: wait until event appear
            except:
                pass
            else:
                for key, mask in event:
                    if key.data == None:     # client start connects to server (key.data is None = not registered)
                        self.start_connect(key.fileobj)
                    else:                   # service connects
                        self.service_connect(key, mask)
        if (not self.connect_status):
            logging.debug('Child thread running listen task ended')

    def stop_listen(self):
        s = self.sel.get_map()
        keys = [i for i in s]
        fileobjs = [s[i] for i in keys]
        # None tell except server_socket
        socks = [file_obj[0] for file_obj in fileobjs if file_obj[3] != None]
        # for short, but not use because of readability
        #_socks = [s[i][0] for i in s if s[i][3] != None]
        for sock in socks:
            logging.debug('Stop connection with {}'.format(sock.getpeername()))
            sock.close()
            self.sel.unregister(sock)
        # self.server_sock.shutdown(socket.SHUT_RDWR)
        self.connect_status = 0
        self.server_sock.close()
        self.sel.unregister(self.server_sock)
        logging.debug('Stop listening')

    def start_connect(self, _sock):
        _connect, _address = _sock.accept()  # accpet connection from client
        _connect.setblocking(False)         # set sock not block
        _data = _address
        _event = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.sel.register(_connect, events=_event, data=_data)        # register this connect to sel, with wait-event are both read & write
        self.connect_status += 1
        logging.debug('Start connection with {}'.format(_address))

    def stop_connect(self, _sock):
        self.sel.unregister(_sock)
        self.connect_status -= 1
        _sock.close()

    def service_connect(self, _key, _mask):
        _sock = _key.fileobj
        _address = _key.data
        if _mask & selectors.EVENT_READ:
            try:
                recv_message = _sock.recv(1024)  # read data
                recv_message = json.loads(recv_message.decode('utf8'))
            except ConnectionResetError:
                logging.debug('Lost connection from {}'.format(_address))
                self.stop_connect(_sock)
            else:
                if recv_message and recv_message['request'] != 'close_connection':
                    if recv_message['request'] == 'ping':
                        logging.debug('PING from {}'.format(_address))
                    else:
                        logging.debug('Message from {}: {}'.format(_address, recv_message['request']))
                        self.handle_message(_sock, recv_message)
                else:
                    logging.debug('Closing connection to {}'.format(_address))
                    self.stop_connect(_sock)

        if _mask & selectors.EVENT_WRITE:
            pass

    def handle_message(self, _sock, recv_message):
        request_code = recv_message['request']
        logging.debug('requét is {}'.format(recv_message))

        if request_code == 'signup':
            # implement sql lookup and respond for sign-in request
            username = recv_message['username']
            password = recv_message['password']
            if self.SQL.add_user(username, password) == True:
                message_to_send = {'request': 'signup', 'status': 'ok'}
                _sock.sendall(json.dumps(message_to_send).encode('utf8'))
                logging.debug('signup-ok')
            else:
                message_to_send = {'request': 'signup', 'status': 'failed'}
                _sock.sendall(json.dumps(message_to_send).encode('utf8'))

        elif request_code == 'login':
            # implement sql lookup and respond for sign-up request
            username = recv_message['username']
            password = recv_message['password']
            if self.SQL.login(username, password) == True:
                message_to_send = {'request': 'login', 'status': 'ok'}
                _sock.sendall(json.dumps(message_to_send).encode('utf8'))
                self.is_loggedin = True
            else:
                message_to_send = {'request': 'login', 'status': 'failed'}
                _sock.sendall(json.dumps(message_to_send).encode('utf8'))

        elif request_code == 'search':
            book_list = self.SQL.get_book_list(recv_message['type'], recv_message['value'].upper())
            message_to_send = {'request': 'search'}
            if len(book_list) == 0:
                message_to_send['status'] = 'error'
            else:
                message_to_send['status'] = 'ok'
                message_to_send['books'] = book_list
            _sock.sendall(json.dumps(message_to_send).encode('utf-8'))
            _sock.sendall('////'.encode('utf-8'))

        elif request_code == 'down' or request_code == 'view':
            # implement sql lookup and respond for downloading book request
            ID = recv_message['ID']
            message_to_send = {'request': 'down'}
            filelocation = self.SQL.get_book_link(ID)
            filelocation = 'books/a.txt'
            try:
                book_stream = open(filelocation, 'rt')
            except IOError:
                message_to_send['status'] = 'error'
            else:
                s = book_stream.read()
                book_stream.close()
                message_to_send['status'] = 'ok'
                message_to_send['book'] = s
            _sock.sendall(json.dumps(message_to_send).encode('utf-8'))
            _sock.sendall('////'.encode('utf-8'))

        elif request_code == 'logout':
            self.is_loggedin = False


if __name__ == '__main__':
    host = '0.0.0.0'    # all network interface
    port = 65432
    server_connection = ServerConnection(host, port)
    server_connection.start_listen()
