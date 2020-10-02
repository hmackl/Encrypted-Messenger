import socket
import tkinter as tk
import threading
import math
import random
import prime

soc = socket.socket()

def binEnc(string):
    return '.'.join(format(ord(i), 'b') for i in string)

def binDec(binary):
    string = ''
    if binary:
        for i in binary.split('.'):
            string += chr(int(i, 2))
    return string

class connectWindow(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.createWidgets()
        self.serverIP = ''

    def createWidgets(self):
        self.serverLabel = tk.Label(self, text='Server: ')
        self.serverLabel.grid(row=0, column=0)
        self.server = tk.Entry(self)
        self.server.insert(0, socket.getfqdn())
        self.server.grid(row=0, column=1)
        self.UsernameLabel = tk.Label(self, text='Username: ')
        self.UsernameLabel.grid(row=1, column=0)
        self.username = tk.Entry(self)
        self.username.grid(row=1, column=1)
        self.PasswordLabel = tk.Label(self, text='Password: ')
        self.PasswordLabel.grid(row=2, column=0)
        self.password = tk.Entry(self)
        self.password.grid(row=2, column=1)
        self.password.bind('<Return>', self.submit)
        self.status = tk.StringVar()
        self.statusLabel = tk.Label(self, textvariable=self.status, fg='Red')
        self.submitButton = tk.Button(self, text='Connect', command=self.submit)
        self.submitButton.grid(row=4, columnspan=2)
        self.pad = tk.Label(self)

    def submit(self, event = False):
        try:
            if self.serverIP != self.server.get():
                soc.connect((self.server.get(), 6969))
                self.serverIP = self.server.get()
            req = '00|%s|%s' % (binEnc(self.username.get()), 
                                binEnc(self.password.get()))
            soc.send(req.encode())
            status = soc.recv(2056)
            if status == b'200':
                print('Connected')
                app.msg['state'] = 'normal'
                app.recipient['state'] = 'normal'
                app.privateKey = 0
                for c in self.password.get(): app.privateKey += ord(c)
                app.username = self.username.get()
                root.title('Private Messaging - ' + self.username.get())
                threading.Thread(target=app.receive).start()
                self.master.destroy()
            elif status == b'401':
                print('Wrong password')
        except:
            self.status.set('Connection Failed: Server Not Found')
            self.statusLabel.grid(row=3, columnspan=2)
        return 'break'

class chatWindow(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.chats = []
        self.master = master
        self.pack()
        self.createWidgets()
        self.connect()

    def placeholder(self, event):
        event.widget.delete('0.0', 'end')
        event.widget.unbind('<Button-1>')

    def createWidgets(self):
        self.recipient = tk.Text(self, height=1, width=40)
        self.recipient.insert('0.0', 'Press <Return> to Connect to User')
        self.recipient['state'] = 'disabled'
        self.recipient.pack(side='top')
        self.recipient.bind('<Button-1>', self.placeholder)
        self.recipient.bind('<Return>', self.link)
        self.log = tk.Text(self, height=30, width=40, state='disabled')
        self.log.pack(side='top')
        self.msg = tk.Text(self, height=10, width=40)
        self.msg.insert('0.0', 'Press <Return> to send message')
        self.msg['state'] = 'disabled'
        self.msg.pack(side='top')
        self.msg.bind('<Button-1>', self.placeholder)
        self.msg.bind('<Return>', self.send)

    def connect(self):
        self.connectWindow = tk.Toplevel(self.master)
        self.app = connectWindow(self.connectWindow)
        self.connectWindow.attributes('-topmost', True)

    def link(self, event):
        self.pubKeys = self.genKey()
        keys = self.pubKeys
        keys.append(keys[1] ** int(self.privateKey) % keys[0])
        req = '01|%s|%s|%s|%s' % (binEnc(self.recipient.get('0.0', 'end-1c')), keys[0], keys[1], keys[2])
        soc.send(req.encode())
        
    def send(self, event):
        msg = self.encrypt(self.encryptionKey, self.msg.get('0.0', 'end-1c'))
        self.msg.delete('0.0', 'end')
        req = '02|%s|%s' % (binEnc(self.recipient.get('0.0', 'end-1c')), binEnc(msg))
        soc.send(req.encode())
        self.log['state'] = 'normal'
        self.log.insert('end', self.username + ': ' + msg + '\n')
        self.log['state'] = 'disabled'
        return 'break'

    def receive(self):
        while 1:
            msg = soc.recv(2056).decode()
            msg = msg.split('|')
            if msg[0] == '404':
                print('Client not available')
            elif msg[0] == '01':
                print('Connection request recieved from: %s (%s, %s, %s)' % (binDec(msg[1]), msg[2], msg[3], msg[4]))
                print('Encryption Key: ' + str(int(msg[4]) ** self.privateKey % int(msg[2])))
                self.encryptionKey = str(int(msg[4]) ** self.privateKey % int(msg[2]))
                req = '01.1|%s|%s' % (msg[1], (int(msg[3]) ** self.privateKey % int(msg[2])))
                soc.send(req.encode())
            elif msg[0] == '01.1':
                print('Connection Request Fufilled: ' + msg[2])
                print('Encryption Key: ' + str(int(msg[2]) ** self.privateKey % self.pubKeys[0]))
                self.encryptionKey = int(msg[2]) ** self.privateKey % self.pubKeys[0]
            elif msg[0] == '02':
                self.log['state'] = 'normal'
                self.log.insert('end', binDec(msg[1]) + ': ' + self.decrypt(self.encryptionKey, binDec(msg[2]).split('.')) + '\n')
                self.log.see('end')
                self.log['state'] = 'disabled'

    def encrypt(self, key, plainText):
        return '.'.join(str(ord(plainText[i]) ^ int(str(key)[i])) for i in range(len(plainText)))

    def decrypt(self, key, text):
        return ''.join(chr(int(text[i]) ^ int(str(key)[i])) for i in range(len(text)))

    def genKey(self):
        keys = [0, -1]
        while keys[1] == -1:
            keys[0] = prime.prime()
            keys[1] = prime.primitiveRoot(keys[0])
        return keys

root = tk.Tk()
root.title('Private Messaging')
root.resizable(False, False)
app = chatWindow(master=root)
app.mainloop()
