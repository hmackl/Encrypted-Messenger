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
    dbCursor.execute(
        'INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
    dbConn.commit()

#addUser('Harry', 'MyPassword')


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
                if data[0] == '01':
                    clients[data[1]].send(self.binEnc(self.username), data[2])
                elif data[0] == '00':
                    if self.getUser(self.binDec(data[1])) == self.binDec(data[2]):
                        self.conn.send(b'200')
                        self.username = self.binDec(data[1])
                        clients[self.username] = clients.pop(host[0])
                        print(self.username + ' Logged in')
                    else:
                        self.conn.send(b'401')
            except Exception as e:
                if e != 'dc':
                    print(e)
                self.conn = False
                print(self.host[0] + ' Disconnected')

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

    def send(self, username, message):
        data = '01|%s|%s' % (username, message)
        self.conn.send(data.encode())


while 1:
    conn, host = soc.accept()
    print(host[0] + ' Connected')
    clients[host[0]] = ClientThread(conn, host)
    clients[host[0]].start()
