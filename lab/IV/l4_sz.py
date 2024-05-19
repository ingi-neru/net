import socket
import threading

host = '127.0.0.1'
port = 44454

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()
print("Server is listening on port {}".format(port))
clients = []
nicknames = []

options = ['/broadcast', '/exit', '/clients', '/users', '/set_broadcast', '/recipient', '/help']
server_rules = 'You can use the following commands: \n/exit - to disconnect from the server\n/clients - to see the current users on the server\n/set_broadcast - set messaging mode to broadcast\n/recipient - to send a message to a specific user\n/help - to see this message again\ninitial messaging mode is broadcast\n'

def broadcast(message, sender):
    for client in clients:
        if client != sender:
            client.send(message.encode())

def private_message(message, recipient):
    message = '<private> ' + message
    recipient_client = None
    for client, nickname in zip(clients, nicknames):
        if nickname == recipient:
            recipient_client = client
            break
    recipient_client.send(message.encode())

def change_recipient(client, recipient):
    if recipient in nicknames:
        response = '/recipient changed to ' + recipient
        client.send(response.encode())
    else:
        client.send('No such recipient on server!'.encode())

def send_clients(client):
    response = 'Current list of clients: ' + ', '.join(nicknames)
    client.send(response.encode())

def handle(client):
    while True:
        try:
            message = client.recv(1024).decode()
            header = message.split(' ')[0]
            if (len(message.split(' ')) < 2 and message not in ["/clients", "/exit", "/help", "/set_broadcast"]):
                print("No message info found")
            else:
                content = message.split(' ')[1:]
            
            if message == "/exit":
                raise ValueError
            if message.startswith('/') and message.split(' ')[0] not in options:
                client.send("No such command found! Use /help to see the list of available commands.".encode())
            elif header == "/broadcast":
                broadcast('{} {}'.format(content[0], ' '.join(content[1:])), client)
            elif header == "/recipient":
                change_recipient(client, content[0])
            elif header == "/set_broadcast":
                response = '/set_broadcast success'
                client.send(response.encode())
            elif header == "/clients":
                send_clients(client)
            elif message == "/help":
                client.send(server_rules.encode())
            else:
                private_message(' '.join(content), header)
        except ValueError:
            client.send('/exit'.encode())
            index = clients.index(client)
            nickname = nicknames[index]
            print('{} left!'.format(nickname))
            nicknames.remove(nickname)
            clients.remove(client)
            break
        except Exception as e:
            print("Error:", e)
            if client:
                client.close()
            break

def receive():
    while True:
        try:
            client, address = server.accept()
            print("New connection from {}".format(str(address)))

            client.send('NICK'.encode())
            nickname = client.recv(1024).decode()
            while nickname in nicknames:
                client.send('Nickname already taken!'.encode())
                nickname = client.recv(1024).decode()
            client.send('NICK OK'.encode())
            nicknames.append(nickname)
            clients.append(client)

            print("Chosen nickname: {}".format(nickname))
            broadcast("{} joined!".format(nickname), client)
            client.send('Succesfully connected to server!'.encode())
            response = 'Welcome to the server!' + server_rules
            client.send(response.encode())

            thread = threading.Thread(target=handle, args=(client,))
            thread.start()
        except KeyboardInterrupt:
            print("Server shutting down...")
            for client in clients:
                client.send('/exit'.encode())
            server.close()
            break
        except Exception as e:
            print("Error:", e)
            break
receive()
