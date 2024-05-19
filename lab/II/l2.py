from socket import *
import threading
import os.path
import mimetypes
shutdown_flag = False
def handle_client(clientsocket):
    #clientsocket.settimeout(5)
    global shutdown_flag
    keepalive = True
    while keepalive:
        try:
            message = clientsocket.recv(4096).decode()
            chunks = message.split(' ')
            if len(chunks) >= 2:
                path = '.' + chunks[1]

                print('Process with id ' + str(threading.get_native_id()) + ' is requesting file ' + path)
                # data = ''
                if os.path.isfile(path) or path == './':
                    data = 'HTTP/1.1 200 OK\r\n'
                    if path == './l2.py' or path == './':
                        path = './welcome.html'
                        if path == './':
                            data += 'Content-type: text/html\r\n'
                        else:
                            data += 'Content-type: ' + mimetypes.guess_type(path)[0] + '; charset=utf-8\r\n'
                else:
                    data = 'HTTP/1.1 404 File Not Found\r\n'
                    path = './error404.html'


                data += 'Content-length: ' + str(os.path.getsize(path)) + '\r\n'
                if 'Connection: close' in message:
                    data += 'Connection: close\r\n'
                    break
                else:
                    data += 'Connection: keep-alive\r\n'
                data += '\r\n'
                data = data.encode()

                with open(path, 'rb') as f:
                    file_data = f.read()
                clientsocket.send(data + file_data)

                if 'Connection: close' in message:
                    print('Shutting down connection with process: ' + str(threading.get_native_id()))
                    clientsocket.close()
                    keepalive = False
        except KeyboardInterrupt:
            print('\nShutting down...')
            shutdown_flag = True
            keepalive = False
        except Exception as e:
            print('Error in process ' + str(threading.get_native_id()) + ':', e)
            clientsocket.close()
            keepalive = False

def webserver():
    global shutdown_flag
    serversocket = socket(AF_INET, SOCK_STREAM)
    serversocket.bind(('', 8080))
    serversocket.listen(5)
    #serversocket.settimeout(5)
    print('Server is now running on port 8080')
    while not shutdown_flag:
        try:
            (clientsocket, address) = serversocket.accept()
            print('Client with address ' + str(address) + ' connected to the server')
            client_handler = threading.Thread(target=handle_client, args=(clientsocket,))
            client_handler.start()
        except KeyboardInterrupt:
            print('\nShutting down...')
            shutdown_flag = True
        except Exception as e:
            print('Error in main :', e)
            shutdown_flag = True

webserver()
