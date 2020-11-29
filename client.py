import socket
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog 
import threading
import math
import random

soc = socket.socket()

def binEnc(string):
    return '.'.join(format(ord(i), 'b') for i in string)

def binDec(binary):
    string = ''
    if binary:
        for i in binary.split('.'):
            string += chr(int(i, 2))
    return string

class GenerateWindow(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.createWidgets()

    def createWidgets(self):
        self.UsernameLabel = tk.Label(self, text='Username: ')
        self.UsernameLabel.grid(row=0, column=0)
        self.username = tk.Entry(self)
        self.username.insert(0, 'admin')
        self.username.grid(row=0, column=1)
        self.PasswordLabel = tk.Label(self, text='Password: ')
        self.PasswordLabel.grid(row=1, column=0)
        self.password = tk.Entry(self, show='*')
        self.password.insert(0, 'adpass')
        self.password.grid(row=1, column=1)
        self.bitsLabel = tk.Label(self, text='Size of Key: ')
        self.bitsLabel.grid(row=2, column=0)
        self.s = tk.StringVar()
        self.bits = ttk.Combobox(self, width=5, textvariable=self.s, state='readonly')
        self.bits['values'] = ('512', '1024', '2048', '4096')
        self.bits.current(0)
        self.bits.grid(row=2, column=1)
        self.generateButton = tk.Button(self, text='Generate Key', command=self.generate)
        self.generateButton.grid(row=3, columnspan=2)
        
    def generate(self):
        print(self.bits)

class ConnectWindow(tk.Frame):
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
        self.UsernameLabel.grid(row=2, column=0)
        self.username = tk.Entry(self)
        self.username.insert(0, 'admin')
        self.username.grid(row=2, column=1)
        self.PasswordLabel = tk.Label(self, text='Password: ')
        self.PasswordLabel.grid(row=3, column=0)
        self.password = tk.Entry(self, show='*')
        self.password.insert(0, 'adpass')
        self.password.grid(row=3, column=1)
        self.password.bind('<Return>', self.submit)
        self.status = tk.StringVar()
        self.statusLabel = tk.Label(self, textvariable=self.status, fg='Red')
        self.openButton = tk.Button(self, text='Open Key', command=self.openKey)
        self.openButton.grid(row=4, columnspan=2)
        self.submitButton = tk.Button(self, text='Connect', command=self.submit)
        self.submitButton.grid(row=5, columnspan=2)
        self.pad = tk.Label(self)
    
    def openKey(self):
        keyDir = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
        keyFile = open(keyDir, 'r')

    def submit(self, event=False):
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
                #root.lift()
            elif status == b'401':
                print('Wrong password')
        except:
            self.status.set('Connection Failed: Server Not Found')
            self.statusLabel.grid(row=3, columnspan=2)
        return 'break'

class ChatWindow(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.chats = []
        self.master = master
        self.createWidgets()
        self.pack()
        
    def deletePlaceholder(self, event):
        if (event.widget['height'] == 1 and event.widget.get() == 'Press <Return> to Connect to User'):
            event.widget.delete(0, 'end')
        elif (event.widget['height'] == 10 and event.widget.get('0.0', 'end-1c') == 'Press <Return> to Send Message'):
            event.widget.delete('0.0', 'end')

    def putPlaceholder(self, event):
        if event.widget['height'] == 1:
            if event.widget.get() == '':
                event.widget.insert(0, 'Press <Return> to Connect to User')
        elif event.widget['height'] == 10:
            if event.widget.get('0.0', 'end-1c') == '':
                event.widget.insert('0.0', 'Press <Return> to Send Message')
    
    def focusMsg(self, event):
        self.msg.focus_set()

    def createWidgets(self):
        self.menu = tk.Menu(self)
        self.homeMenu = tk.Menu(self.menu, tearoff=0)
        self.homeMenu.add_command(label='Connect', command=self.connect)
        self.homeMenu.add_command(label='Create Profile', command=self.createProfile)
        self.homeMenu.add_separator()
        self.homeMenu.add_command(label='Disconnect', command=self.destroy)
        self.homeMenu.add_command(label='Exit', command=self.master.destroy)
        self.menu.add_cascade(label='Home', menu=self.homeMenu)
        self.master.config(menu=self.menu)
        self.recipient = ttk.Combobox(self, font='TkFixedFont', height=1)
        self.recipient.insert(0, 'Press <Return> to Connect to User')
        self.recipient['state'] = 'disabled'
        self.recipient.pack(side='top', fill='x')
        self.recipient.bind('<FocusIn>', self.deletePlaceholder)
        self.recipient.bind('<FocusOut>', self.putPlaceholder)
        # self.recipient.bind('<Return>', self.link)
        self.log = tk.Text(self, height=30, width=40, state='disabled')
        self.log.pack(side='top')
        self.msg = tk.Text(self, height=10, width=40)
        self.msg.insert('0.0', 'Press <Return> to Send Message')
        self.msg['state'] = 'disabled'
        self.msg.pack(side='top')
        self.log.bind('<FocusIn>', self.focusMsg)
        self.msg.bind('<FocusIn>', self.deletePlaceholder)
        self.msg.bind('<FocusOut>', self.putPlaceholder)
        self.msg.bind('<Return>', self.send)

    def connect(self):
        self.ConnectWindow = tk.Toplevel(self.master)
        self.liftButton = tk.Button(self, text='Lift Off!!', command=self.ConnectWindow.lift)
        self.liftButton.pack()
        self.app = ConnectWindow(self.ConnectWindow)

    def createProfile(self):
        self.GenerateWindow = tk.Toplevel(self.master)
        self.app = GenerateWindow(self.GenerateWindow)

    # def link(self, event):
    #     self.pubKeys = self.genKey()
    #     keys = self.pubKeys
    #     keys.append(keys[1] ** int(self.privateKey) % keys[0])
    #     req = '01|%s|%s|%s|%s' % (binEnc(self.recipient.get()), keys[0], keys[1], keys[2])
    #     soc.send(req.encode())
        
    # def send(self, event):
    #     msg = self.msg.get('0.0', 'end-1c')
    #     encrypted = self.encrypt(self.encryptionKey, msg)
    #     self.msg.delete('0.0', 'end')
    #     req = '02|%s|%s' % (binEnc(self.recipient.get()), binEnc(encrypted))
    #     soc.send(req.encode())
    #     self.log['state'] = 'normal'
    #     self.log.insert('end', self.username + ': ' + msg + '\n')
    #     self.log['state'] = 'disabled'
    #     return 'break'

    # def receive(self):
    #     while 1:
    #         msg = soc.recv(2056).decode()
    #         msg = msg.split('|')
    #         if msg[0] == '404':
    #             print('Client not available')
    #         elif msg[0] == '01':
    #             print('Connection request recieved from: %s (%s, %s, %s)' % (binDec(msg[1]), msg[2], msg[3], msg[4]))
    #             print('Encryption Key: ' + str(int(msg[4]) ** self.privateKey % int(msg[2])))
    #             self.encryptionKey = str(int(msg[4]) ** self.privateKey % int(msg[2]))
    #             req = '01.1|%s|%s' % (msg[1], (int(msg[3]) ** self.privateKey % int(msg[2])))
    #             soc.send(req.encode())
    #         elif msg[0] == '01.1':
    #             print('Connection Request Fufilled: ' + msg[2])
    #             print('Encryption Key: ' + str(int(msg[2]) ** self.privateKey % self.pubKeys[0]))
    #             self.encryptionKey = int(msg[2]) ** self.privateKey % self.pubKeys[0]
    #         elif msg[0] == '02':
    #             self.log['state'] = 'normal'
    #             self.log.insert('end', binDec(msg[1]) + ': ' + self.decrypt(self.encryptionKey, binDec(msg[2]).split('.')) + '\n')
    #             self.log.see('end')
    #             self.log['state'] = 'disabled'

    # def encrypt(self, key, plainText):
    #     return '.'.join(str(ord(plainText[i]) ^ int(str(key)[i])) for i in range(len(plainText)))

    # def decrypt(self, key, text):
    #     return ''.join(chr(int(text[i]) ^ int(str(key)[i])) for i in range(len(text)))

    # def genKey(self):
    #     keys = [0, -1]
    #     while keys[1] == -1:
    #         keys[0] = prime.prime()
    #         keys[1] = prime.primitiveRoot(keys[0])
    #     return keys

root = tk.Tk()
root.title('Private Messaging')
root.resizable(False, False)
app = ChatWindow(master=root)
app.mainloop()
