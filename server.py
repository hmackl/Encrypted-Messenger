import socket

soc = socket.socket()
host = socket.getfqdn()
soc.bind((host, 6969))

soc.listen()

conn, host = soc.accept()
print(host[0] + ' Connected')
while conn:
    data = conn.recv(2056)
    print('Recieved: ' + data.decode())
    conn.sendall(data)
