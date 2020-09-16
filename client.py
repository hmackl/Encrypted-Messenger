import socket

soc = socket.socket()
soc.connect((socket.getfqdn(), 6969))

while 1:
    soc.send(input().encode())
    data = soc.recv(2056)
    print('Recieved: ' + data.decode())