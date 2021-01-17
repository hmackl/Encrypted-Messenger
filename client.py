import socket
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog 
from tkinter import messagebox
import threading
import crypto
import time

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
        rsa = crypto.RSA()
        aes = crypto.AES()
        bits = int(self.bits['values'][self.bits.current()])
        keys = rsa.generateKey(bits)
        if (self.password.get() != ''):
            password = aes.keySchedule(self.password.get())
            cypher = aes.encrypt(self.username.get().encode('utf-8').hex(), password)
            keyFile = filedialog.asksaveasfile(mode='w+', defaultextension='ckf', title='Select file', filetypes=(('Client Key','*.ckf'), ('All Files','*.*')))
            for i in range(0, len(cypher), 16):
                keyFile.write(' '.join(cypher[i:i+16]) + '\n')
            for i in range(2):
                keyFile.write('-'*47 + '\n')
                keys[i] = aes.encrypt(keys[i][2:], password)
                for j in range(0, len(keys[i]), 16):
                    keyFile.write(' '.join(keys[i][j:j+16]) + '\n')
            keyFile.close()
            messagebox.showinfo('Successful', 'Key Generated Successfully')
            self.master.destroy()

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
        keyFile = filedialog.askopenfile(title = "Select file", filetypes=(("Client Key","*.ckf"), ("All Files","*.*")))
        self.parsed = [[]]
        for line in keyFile:
            line = line.strip('\n')
            if line != '':
                if line == '-'*47:
                    self.parsed.append([])
                else:
                    self.parsed[-1].append([])
                    state = line.split()
                    for row in range(0, len(state), 4):
                        self.parsed[-1][-1].append(state[row:row+4])
        self.focus_force()

    def submit(self, event=False):
        try:
            keys = []
            aes = crypto.AES()
            for key in self.parsed:
                keys.append(aes.decrypt(key, aes.keySchedule(self.password.get())))
            if (bytes.fromhex(keys[0][2:]).decode('utf-8').strip('\x00') != self.username.get()):
                raise Exception()
            try:
                if self.serverIP != self.server.get():
                    soc.connect((self.server.get(), 6969))
                    self.serverIP = self.server.get()
                req = '00|%s|%s' % (binEnc(self.username.get()), keys[1])
                soc.send(req.encode())
                code = int(soc.recv(2056))
                verificationCode = str(pow(code, int(keys[2], 16), int(keys[1], 16)))
                soc.send(verificationCode.encode())
                status = soc.recv(2056)
                if status == b'01':
                    print('Connected')
                    app.key = keys[1:]
                    app.username = self.username.get()
                    app.recipient['state'] = 'readonly'
                    root.title('Private Messaging - ' + self.username.get())
                    threading.Thread(target=app.receive).start()
                    self.master.destroy()
                elif status == b'11':
                    self.status.set('Connection Failed: Client Already Logged In')
                    self.statusLabel.grid(row=6, columnspan=2)
            except Exception as e:
                print(e)
                self.status.set('Connection Failed: Server Not Found')
                self.statusLabel.grid(row=6, columnspan=2)
        except:
            self.status.set('Connection Failed: Incorrect Credentials')
            self.statusLabel.grid(row=6, columnspan=2)
        return 'break'

class AddChat(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.createWidgets()
        self.getUsers()

    def getUsers(self):
        soc.send(b'02')
        while 1:
            soc.send(b'03')
            data = soc.recv(2056)
            data = data.decode().split('|')
            if data[0] == '05' and data[2] != app.key[0]:
                self.userList.insert('', 'end', text=data[1], values=(data[2]))
            elif data[0] == '04': break
        app.listening = True

    def createWidgets(self):
        self.userList = ttk.Treeview(self, columns=('#1'))
        self.userList.column('#0', minwidth=150)
        self.userList.column('#1', minwidth=350, stretch=tk.NO)
        self.userList.heading('#0', text='Alias')
        self.userList.heading('#1', text='Public Key')
        sb = ttk.Scrollbar(self, orient="vertical", command=self.userList.yview)
        sb.pack(side='right', fill='both')
        self.userList.configure(yscrollcommand=sb.set)
        self.userList.bind('<Double-1>', self.addChat)
        self.userList.pack(fill='both')

    def addChat(self, event):
        selection = self.userList.selection()
        key = self.userList.item(selection, 'text') + ' - ' + self.userList.item(selection, 'values')[0][:20] + '...'
        app.recipient['values'] += (key,)
        app.recipient.current(len(app.recipient['values']) - 1)
        app.recipients[key] = self.userList.item(selection, 'values')[0]
        app.updateLog()
        self.master.destroy()

class ChatWindow(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.recipientOptions = ['Start New Chat']
        self.rsa = crypto.RSA()
        self.key = []
        self.username = ''
        self.listening = True
        self.recipients = {}
        self.chats = {}
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
        self.homeMenu.add_command(label='Create Profile', command=self.createProfile)
        self.homeMenu.add_command(label='Connect', command=self.connect)
        self.homeMenu.add_separator()
        self.homeMenu.add_command(label='Exit', command=self.master.destroy)
        self.menu.add_cascade(label='Home', menu=self.homeMenu)
        self.master.config(menu=self.menu)
        self.recipient = ttk.Combobox(self, font='TkFixedFont', values=self.recipientOptions, height=1)
        self.recipient.current(0)
        self.recipient['state'] = 'disabled'
        self.recipient.pack(side='top', fill='x')
        self.recipient.bind('<FocusIn>', self.deletePlaceholder)
        self.recipient.bind('<FocusOut>', self.putPlaceholder)
        self.recipient.bind('<<ComboboxSelected>>', self.combochanged)
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

    def combochanged(self, event):
        if self.recipient.current() == 0:
            self.newChat()
        else:
            self.updateLog()

    def createProfile(self):
        self.GenerateWindow = tk.Toplevel(self.master)
        self.app = GenerateWindow(self.GenerateWindow)
        self.GenerateWindow.resizable(False, False)

    def connect(self):
        self.ConnectWindow = tk.Toplevel(self.master)
        self.app = ConnectWindow(self.ConnectWindow)
        self.ConnectWindow.resizable(False, False)

    def newChat(self):
        self.AddChat = tk.Toplevel(self.master)
        self.app = AddChat(self.AddChat)
        self.AddChat.resizable(False, False)

    def updateLog(self):
        if self.recipient.current() == 0: return
        recipient = self.recipients[self.recipient.get()]
        self.log['state'] = 'normal'
        self.log.delete('1.0', 'end')
        if recipient not in self.chats:
            self.log.insert('end', 'The is the beginning of your DM history\n')
        else:
            t = ''
            for chat in self.chats[recipient]:
                if chat[1] != t:
                    self.log.insert('end', chat[1] + '\n')
                    t = chat[1]
                self.log.insert('end', chat[0] + ': ' + chat[2] + '\n')
        self.log.see('end')
        self.log['state'] = 'disabled'
        self.msg['state'] = 'normal'

    def send(self, event):
        recipient = self.recipients[self.recipient.get()]
        msg = self.msg.get('0.0', 'end-1c')
        t = time.time()
        data = ('06' + '|' + recipient + '|' + 
            self.key[0] + '~' +
            str(self.rsa.encrypt(self.username, recipient)) + '|' +
            str(self.rsa.encrypt(str(t), recipient)) + 
            '|' + str(self.rsa.encrypt(msg, recipient)) + '~' +
            str(self.rsa.encrypt(self.username, self.key[0])) + '|' +
            str(self.rsa.encrypt(str(t), self.key[0])) + 
            '|' + str(self.rsa.encrypt(msg, self.key[0])))
        for d in data.split('|'):
            print(d)
        if recipient not in self.chats:
            self.chats[recipient] = []
        self.chats[recipient].append([self.username, time.strftime('%H:%M', time.localtime(t)), msg])
        self.updateLog()
        soc.send(data.encode())
        self.msg.delete('0.0', 'end')
        return 'break'

    def receive(self):
        while 1:
            if self.listening:
                data = soc.recv(2056).decode()
                data = data.split('|')
                if data[0] == '03':
                    self.listening = False
                elif data[0] == '07':
                    msg = []
                    for i in range(len(data)-2):
                        msg.append(self.rsa.decrypt(data[i+2], self.key[0], self.key[1]))
                    msg[1] = time.strftime('%H:%M', time.localtime(float(msg[1])))
                    if data[1] not in self.chats:
                        self.chats[data[1]] = []
                        self.recipient['values'] += (msg[0] + ' - ' + data[1][:20] + '...',)
                        self.recipients[msg[0] + ' - ' + data[1][:20] + '...'] = data[1]
                    self.chats[data[1]].append(msg)
                    self.updateLog()
                    soc.send(b'04')

root = tk.Tk()
root.title('Private Messaging')
root.resizable(False, False)
app = ChatWindow(master=root)
app.mainloop()
