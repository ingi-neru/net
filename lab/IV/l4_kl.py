import socket
import threading

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 44454))

mode = '/broadcast'
options = ['/exit', '/clients', '/set_broadcast', '/recipient', '/exit', '/help']
nickname = ''

def receive():
    global mode
    global nickname
    while True:
        try:
            message = client.recv(1024).decode()
            if not message:
                client.send('/exit'.encode())
                print("Server closed the connection.")
                break
            if message == 'NICK' or message == 'Nickname already taken!':
                if message == 'Nickname already taken!':
                    print("Nickname already taken! Please choose another one.")
                else:
                    print("Choose your nickname: ")
                nickname = input()
                client.send(nickname.encode())
            elif message == 'NICK OK':
                write_thread = threading.Thread(target=write)
                write_thread.start()
            else:
                header = message.split(' ')[0]
                if header not in options:
                    print(message)
                elif header == "/recipient":
                    status = message.split(' ')[1]
                    if status == "changed":
                        mode = message.split(' ')[-1]
                        print("Recipient successfully changed!")
                    else:
                        print("No such recipient on server, currently sending messages to: " + mode)
                elif header == "/set_broadcast":
                    print("Changing mode to broadcast...")
                    mode = '/broadcast'
                elif message == "/exit":
                    print("Disconnecting from server!")
                    client.close()
                    break
                else:
                    print("The current users on the server are: " + message)
        except ConnectionResetError:
            print("Connection reset by peer.")
            break
        except Exception as e:
            print("An error occurred:", e)
            break


def write():
    global mode
    while True:
        try:
            message = input('')
            header = message.split(' ')[0]
            if message == '/help':
                client.send(message.encode())
            elif header not in options:
                response = mode + ' <' + nickname + '> ' + message
                client.send(response.encode())
            else:
                if message == '/exit':
                    client.send('/exit'.encode())
                    break
        except ConnectionResetError:
            print("Connection reset by peer.")
            break


receive_thread = threading.Thread(target=receive)
receive_thread.start()