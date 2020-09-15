import socket

soc = socket.socket()
host = socket.getfqdn()
soc.bind((host, 6969))

soc.listen(100)

sockets = {}

while 1:
    c, host = soc.accept()
    print(c.recv(2056))
