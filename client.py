import socket
import tkinter as tk
import threading

soc = socket.socket()

def binEncode(string):
    return '.'.join(format(ord(i), 'b') for i in string)

def binDecode(binary):
    string = ''
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
            req = '00|%s|%s' % (binEncode(self.username.get()), 
                                binEncode(self.password.get()))
            soc.send(req.encode())
            status = soc.recv(2056)
            if status == b'200':
                print('Connected')
                app.msg['state'] = 'normal'
                app.recipent['state'] = 'normal'
                app.username = self.username.get()
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
        self.master = master
        self.pack()
        self.createWidgets()
        self.connect()

    def placeholder(self, event):
        print(event)
        self.msg.delete('0.0', 'end')
        self.msg.unbind('<Button-1>')

    def createWidgets(self):
        self.recipent = tk.Entry(self, width=53)
        self.recipent.pack(side='top')
        self.log = tk.Text(self, height=40, width=40, state='disabled')
        self.log.pack(side='top')
        self.msg = tk.Text(self, height=10, width=40)
        self.msg.insert('0.0', 'Press <Return> to send message')
        self.msg['state'] = 'disabled'
        self.msg.bind('<Button-1>', self.placeholder)
        self.msg.pack(side='top')
        self.msg.bind('<Return>', self.send)

    def connect(self):
        self.connectWindow = tk.Toplevel(self.master)
        self.app = connectWindow(self.connectWindow)
        self.connectWindow.attributes('-topmost', True)
        
    def send(self, event):
        msg = self.msg.get('0.0', 'end-1c')
        self.msg.delete('0.0', 'end')
        req = '01|%s|%s' % (self.recipent.get(), binEncode(msg))
        soc.send(req.encode())
        self.log['state'] = 'normal'
        self.log.insert('end', self.username + ': ' + msg + '\n')
        self.log['state'] = 'disabled'
        return 'break'

    def receive(self):
        while 1:
            msg = soc.recv(2056).decode()
            msg = msg.split('|')
            self.log['state'] = 'normal'
            self.log.insert('end', msg[1] + ': ' + msg[2] + '\n')
            self.log['state'] = 'disabled'

root = tk.Tk()
root.title('Private Messaging')
root.resizable(False, False)
app = chatWindow(master=root)
app.mainloop()
