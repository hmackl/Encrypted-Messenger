import socket

soc = socket.socket()
soc.connect((socket.getfqdn(), 6969))

soc.send('Hello world!'.encode())