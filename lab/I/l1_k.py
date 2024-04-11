import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s = input('Add meg a kuldendo szovget:')
client_socket.connect(('', 8080))

print('Connected to server on port 127.0.0.1:8080')
length = len(s)
len = str(len(s)) + ' '
client_socket.send(len.encode())
client_socket.send(s.encode())
if s != "exit":
    recieved_string = str(client_socket.recv(length).decode())
    print('Received the message: ' + recieved_string)
client_socket.close()
