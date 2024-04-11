import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('', 8080))
server_socket.listen()
print('Listening on port 127.0.0.1:8080')
buffer_size = 1024
sep = ' '
while True:
    (client_socket, address) = server_socket.accept()
    print('Connection established with: ' + str(address))
    buf = ''
    while sep not in buf:
        data = client_socket.recv(8).decode()
        buf += data
    txt = buf.split(' ')
    length = int(txt[0])
    input = txt[1]
    bytes_read = len(input)
    while bytes_read <= length:
        data = client_socket.recv(min(buffer_size - bytes_read,buffer_size)).decode()
        print('Received data from ' + str(address) + ': ' + data)
        input += data
        bytes_read += buffer_size

    client_socket.send(input.upper().encode())

    print('Closing connection with: ' + str(address))
    client_socket.close()

    if input == "exit":
        print('Got the message "exit", closing now')
        break

server_socket.close()

