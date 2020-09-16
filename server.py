import socket
import threading

soc = socket.socket()
host = socket.getfqdn()
soc.bind((host, 6969))

soc.listen()

clients = {}

def client_thread(conn, host):
    while conn:
        data = conn.recv(2056)
        print('Recieved: ' + data.decode())
        conn.sendall(data)

while 1:
    conn, host = soc.accept()
    print(host[0] + ' Connected')
    clients[host[0]] = threading.Thread(target=client_thread, args=(conn, host))
    clients[host[0]].start()
