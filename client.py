import socket
import tkinter as tk
import time

# soc = socket.socket()
# soc.connect((socket.getfqdn(), 6969))

class connectWindow(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.createWidgets()

    def createWidgets(self):
        self.server = tk.Entry(self)
        self.server.pack(side='top')
        self.username = tk.Entry(self)
        self.username.pack(side='top')
        self.password = tk.Entry(self)
        self.password.pack(side='top')
        self.username.bind('<Return>', self.submit)

    def submit(self, event):
        print('Submit')
        self.master.destroy()

class chatWindow(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.createWidgets()
        self.connect()

    def createWidgets(self):
        self.log = tk.Text(self, height=40, width=40, state='disabled')
        self.log.pack(side='top')
        self.msg = tk.Text(self, height=10, width=40)
        self.msg.pack(side='top')
        self.msg.bind('<Return>', self.send)

    def connect(self):
        self.connectWindow = tk.Toplevel(self.master)
        self.app = connectWindow(self.connectWindow)
        self.connectWindow.attributes('-topmost', True)

    def send(self, event):
        msg = self.msg.get('0.0', 'end-1c')
        self.msg.delete('0.0', 'end')
        #soc.send(msg.encode())
        return 'break'

root = tk.Tk()
root.title('Private Messaging')
root.resizable(False, False)
app = chatWindow(master=root)
app.mainloop()

# while 1:
#     soc.send(input().encode())
#     data = soc.recv(2056)
#     print('Recieved: ' + data.decode())
