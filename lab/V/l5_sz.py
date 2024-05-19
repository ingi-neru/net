import socket
import sys
import threading
from PIL import Image

host = '127.0.0.1'
port = 12345
max_clients = 8
width = 800
height = 600
max_iter = 1000
along_x = 1
usage = "Usage: python l5_sz.py [-w width] [-h height] [-m max_iter] [-c max_clients] [-d horizontal|vertical h|v]"
if len(sys.argv) % 2 == 0:
    print("Invalid arguments")
    print(usage)
    sys.exit()
else:
    i = 1
    while i < len(sys.argv):
        try:
            if sys.argv[i] == "-w":
                width = int(sys.argv[i + 1])
            elif sys.argv[i] == "-h":
                height = int(sys.argv[i + 1])
            elif sys.argv[i] == "-m":
                max_iter = int(sys.argv[i + 1])
            elif sys.argv[i] == "-c":
                max_clients = int(sys.argv[i + 1])
            elif sys.argv[i] == "-d":
                if sys.argv[i + 1] == "horizontal" or sys.argv[i + 1] == "vertical" or sys.argv[i + 1] == "h" or sys.argv[i + 1] == "v":
                    if (sys.argv[i + 1] == "vertical" or sys.argv[i + 1] == "v"):
                        along_x = 1
                    else:
                        along_x = 0
                else:
                    print("Wrong partitioning direction, will use default (horizontal)")
            else:
                print("Invalid arguments")
                print(usage)
                sys.exit()
            i += 2
        except IndexError:
            print("Invalid arguments")
bytes_per_client = width * height * 3 // max_clients
chunks = [None] * max_clients

def distribute_tasks():
    tasks = []
    if along_x:
        step = height // max_clients
        remaining = height % max_clients
    else:
        step = width // max_clients
        remaining = width % max_clients
    start = 0

    for i in range(max_clients):
        end = start + step
        if remaining > 0:
            end += 1
            remaining -= 1
        tasks.append((width, height, start, end, max_iter, i * 25, along_x))
        start = end

    return tasks

def read_bytes(client_socket, num_bytes):
    data = b''
    while len(data) < num_bytes:
        chunk = client_socket.recv(num_bytes - len(data))
        if chunk == b'':
            raise RuntimeError("Socket connection broken")
        data += chunk
    return data

def handle_client(client_socket, task, index):
    width, height, start_y, end_y, max_iter, color, along_x = task
    print(width, height, start_y, end_y, max_iter, color, along_x)
    client_socket.sendall(f"{width},{height},{start_y},{end_y},{max_iter},{color},{along_x}".encode())
    chunks[index] = read_bytes(client_socket, bytes_per_client)
    client_socket.close()
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(max_clients)

tasks = distribute_tasks()
print("Server is listening on port " + str(port) + "...")
threads = []
index = 0
for task in tasks:
    try:
        client_socket, _ = server_socket.accept()
        print("Client connected")
        thread = threading.Thread(target=handle_client, args=(client_socket, task, index))
        threads.append(thread)
        thread.start()
        index += 1
    except KeyboardInterrupt:
        print("Server is shutting down...")
        break

for thread in threads:
    thread.join()

data = bytearray(width * height * 3)
if (None in chunks or len(chunks) != max_clients):
    print("Server was shut down before all clients finished")
else:
    if not along_x:
        i = 0
        j = 0
        next = width * 3 // max_clients
        while j < width * height * 3:
            for k in range(max_clients):
                data[j:j + next] = chunks[k][i:i + next]
                j += next
            i += next
        image = Image.frombytes("RGB", (width, height), data, 'raw')
        image.show()
    else:
        image = Image.frombytes("RGB", (width, height), b''.join(chunks), 'raw')
        image.show()
server_socket.close()