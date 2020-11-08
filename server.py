import socket
import threading
import sqlite3

def addUser(username, password):
    dbConn = sqlite3.connect('messenger.db')
    dbCursor = dbConn.cursor()
    #dbCursor.execute('CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, username NOT NULL UNIQUE, password NOT NULL)')
    dbCursor.execute(
        'INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
    dbConn.commit()

#addUser('harry', 'hpass')

class ClientThread(threading.Thread):
    def __init__(self, server, conn, host):
        super().__init__()  # overrides parent class 'threading.Thread' __init__
        self.conn = conn
        self.host = host
        self.username = ''
        self.server = server

    def run(self):
        while self.conn:
            try:
                data = self.conn.recv(2056)
                if data == b'':
                    raise Exception('dc')
                data = data.decode().split('|')
                client = self.binDec(data[1])
                if data[0] == '02' and client in self.server.clients:
                    self.server.clients[client].send('02', [self.binEnc(self.username), data[2]])
                elif data[0] == '01.1' and client in self.server.clients:
                    self.server.clients[client].send('01.1', [self.binEnc(self.username), data[2]])
                elif data[0] == '01' and client in self.server.clients:
                    self.server.clients[client].send('01', [self.binEnc(self.username)] + data[2:])
                elif data[0] == '00':
                    if self.getUser(client) == self.binDec(data[2]):
                        self.conn.send(b'200')
                        self.username = client
                        self.server.clients[self.username] = self.server.clients.pop(self.host[0])
                        print(self.username + ' Logged in')
                    else:
                        self.conn.send(b'401')
                else:
                    self.conn.send(b'404')
            except Exception as e:
                if e == Exception('dc'):
                    print(self.host[0] + ' Disconnected')
                else:
                    print('Error: ' + str(e))
                self.conn = False

    def binDec(self, binary):
        string = ''
        for i in binary.split('.'):
            string += chr(int(i, 2))
        return string

    def binEnc(self, string):
        return '.'.join(format(ord(i), 'b') for i in string)

    def getUser(self, username):
        dbConn = sqlite3.connect('messenger.db')
        dbCursor = dbConn.cursor()
        dbCursor.execute(
            'SELECT password FROM users WHERE username=?', (username,))
        res = dbCursor.fetchone()
        if res:
            return res[0]
        else:
            return False

    def send(self, opcode, oprands):
        data = '%s' % (opcode)
        for oprand in oprands:
            data += '|%s' % (oprand)
        self.conn.send(data.encode())

class Server(threading.Thread):
    def __init__(self, port):
        super().__init__()  # overrides parent class 'threading.Thread' __init__
        self.port = port
        self.soc = socket.socket()
        self.host = socket.getfqdn()
        self.soc.bind((self.host, port))
        self.soc.listen()
        self.clients = {}
        self.listen()
    
    def listen(self):
        while 1:
            self.conn, self.host = self.soc.accept()
            print(self.host[0] + ' Connected')
            self.clients[self.host[0]] = ClientThread(self, self.conn, self.host)
            self.clients[self.host[0]].start()

server = Server(6969)
server.start()
