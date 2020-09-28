import socket
import threading
import sqlite3

soc = socket.socket()
host = socket.getfqdn()
soc.bind((host, 6969))
soc.listen()

clients = {}


def addUser(username, password):
    dbConn = sqlite3.connect('messenger.db')
    dbCursor = dbConn.cursor()
    #dbCursor.execute('CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, username NOT NULL UNIQUE, password NOT NULL)')
    dbCursor.execute(
        'INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
    dbConn.commit()

#addUser('harry', 'hpass')


class ClientThread(threading.Thread):
    def __init__(self, conn, host):
        super().__init__()  # overrides parent class 'threading.Thread' __init__
        self.conn = conn
        self.host = host
        self.username = ''

    def run(self):
        while self.conn:
            try:
                data = self.conn.recv(2056)
                if data == b'':
                    raise Exception('dc')
                data = data.decode().split('|')
                if data[0] == '02':
                    if self.binDec(data[1]) in clients:
                        clients[self.binDec(data[1])].send(
                            '02', self.binEnc(self.username) + '|' + data[2])
                    else:
                        self.conn.send(b'404')
                elif data[0] == '01.1':
                    if self.binDec(data[1]) in clients:
                        clients[self.binDec(data[1])].send(
                            '01.1', self.binEnc(self.username) + '|' + data[2])

                elif data[0] == '01':
                    if self.binDec(data[1]) in clients:
                        clients[self.binDec(data[1])].send('01', self.binEnc(self.username) +
                                                           '|' + data[2] +
                                                           '|' + data[3] +
                                                           '|' + data[4])
                    else:
                        self.conn.send(b'404')
                elif data[0] == '00':
                    if self.getUser(self.binDec(data[1])) == self.binDec(data[2]):
                        self.conn.send(b'200')
                        self.username = self.binDec(data[1])
                        clients[self.username] = clients.pop(host[0])
                        print(self.username + ' Logged in')
                    else:
                        self.conn.send(b'401')
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

    def send(self, code, message):
        data = '%s|%s' % (code, message)
        self.conn.send(data.encode())


while 1:
    conn, host = soc.accept()
    print(host[0] + ' Connected')
    clients[host[0]] = ClientThread(conn, host)
    clients[host[0]].start()
