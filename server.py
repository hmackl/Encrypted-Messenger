import socket
import threading
import sqlite3
from time import time_ns

'''
Connection Codes:
    00 <- Client Requesting Connection
    01 -> Connection Successful
    02 <- Request Clients
    03 <-> Ready
    04 <- Complete
    05 <- Client
    06 <- Message from Sender
    07 -> Message to Receipient
    08 -> Confirmation of Receipt of Server
    09 -> Confirmation of Receipt of Receipient
    10 <- Request Messages
    11 -> Client Already Logged in

Packet Structure:
    Message from Sender:
        Code|Recipient Key|Sender Key~Encrypted Recipient Username|Encrypted Time|Encrypted Message
                                     ~Encrypted Recipeint Username|Encrypted Time|Encrypted Message
    Message to Recipient:
        Code|Sender Key|Encrypted Username|Encrypted Time|Encrypted Message
'''

class ClientThread(threading.Thread):
    def __init__(self, server, conn, host):
        super().__init__()  # overrides parent class 'threading.Thread' __init__
        self.conn = conn
        self.host = host
        self.id = host[0]
        self.username = ''
        self.server = server
        self.verified = False
        self.readyToSend = True

    def run(self):
        while self.conn:
            try:
                rawData = self.conn.recv(4096)
                if rawData == b'':
                    raise Exception('dc')
                data = rawData.decode().split('|')
                if data[0] == '00':
                    time = time_ns()
                    self.conn.send(str(time).encode())
                    code = self.conn.recv(2056)
                    encoded = pow(int(code), 65537, int(data[2], 16))
                    if encoded == time:
                        if data[2] not in self.server.clients.keys():
                            self.verified = True
                            self.server.clients[data[2]] = self.server.clients.pop(self.host[0])
                            self.id = data[2]
                            self.username = self.binDec(data[1])
                            self.conn.send(b'01')
                            for row in self.server.sql.execute('SELECT * FROM messages WHERE recipient = ? OR sender = ?', (self.id, self.id)):
                                while 1:
                                    if self.readyToSend == True:
                                        self.readyToSend = False
                                        sender = 0
                                        if row[1] == self.id:
                                            sender = 1
                                        users = row[0:2]
                                        row = row[sender+2].split('|')
                                        if users[sender] in self.server.clients:
                                            data = ('07|%s|%s|%s|%s' % (users[(sender+1) % 2], row[0], row[1], row[2]))
                                            self.conn.send(data.encode())
                                        break
                                    if self.conn.recv(2056) == b'04':
                                        self.readyToSend = True
                        else:
                            self.conn.send(b'11')
                    else:
                        print('Verification Failure. Possible Attack?')
                elif data[0] == '02' and self.verified:
                    self.conn.send(b'03')
                    for client in self.server.clients:
                        data = self.conn.recv(2056)
                        if data == b'03':
                            self.conn.send(('05|%s|%s' % (self.server.clients[client].username, client)).encode())
                    data = self.conn.recv(2056)
                    if data == b'03':
                        self.conn.send(b'04')
                elif data[0] == '06' and self.verified:
                    rawData = rawData.decode().split('~')
                    meta = rawData[0].split('|')
                    self.server.sql.execute('INSERT INTO messages VALUES ("%s", "%s", "%s", "%s")' % (meta[1], meta[2], rawData[1], rawData[2]))
                    if meta[1] in self.server.clients:
                        msg = rawData[1].split('|')
                        data = ('07|%s|%s|%s|%s' % (meta[2], msg[0], msg[1], msg[2]))
                        self.server.clients[meta[1]].conn.send(data.encode())
                elif data[0] == '04':
                    self.readyToSend = True
            except Exception as e:
                if e == Exception('dc'):
                    print(self.host[0] + ' Disconnected')
                else:
                    print('Error: ' + str(e))
                self.conn = False
                self.server.sql.commit()
                self.server.clients.pop(self.id)

    def binDec(self, binary):
        string = ''
        for i in binary.split('.'):
            string += chr(int(i, 2))
        return string

    def binEnc(self, string):
        return '.'.join(format(ord(i), 'b') for i in string)

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
        self.sql = sqlite3.connect('messages.db', check_same_thread=False)
        self.sql.execute('''CREATE TABLE IF NOT EXISTS messages (recipient TEXT NOT NULL, sender TEXT NOT NULL, message_r TEXT NOT NULL, message_s TEXT NOT NULL);''')
        self.listen()     

    def listen(self):
        print('Server Running')
        while 1:
            self.conn, self.host = self.soc.accept()
            print(self.host[0] + ' Connected')
            self.clients[self.host[0]] = ClientThread(self, self.conn, self.host)
            self.clients[self.host[0]].start()

server = Server(6969)
server.start()
