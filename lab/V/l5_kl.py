import socket
from PIL import Image

host = '127.0.0.1'
port = 12345

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host, port))
data = client_socket.recv(1024).decode()
result = bytearray()
width, height, start_y, end_y, max_iter, color, along_x = map(int, data.split(','))
if along_x == 0:
    start_x, end_x = start_y, end_y

def mandelbrot(c, max_iter):
    z = 0
    n = 0
    while abs(z) <= 2 and n < max_iter:
        z = z*z + c
        n += 1
    return n

def vertical():
    for y in range(start_y, end_y):
        for x in range(width):
            c = complex((x - width / 2) * 4 / width, (y - height / 2) * 4 / height)
            color_value = mandelbrot(c, max_iter)
            if color_value < max_iter:
                color_value = (0, 0, 0)
            else:
                color_value = ((color_value + color) % 255, (color_value * 2 + color) % 255, (color_value * 3 + color) % 255)
            result.extend(color_value)

def horizontal():
    for y in range(0,height):
        c_y = (y - height / 2) * 4 / height
        for x in range(start_x, end_x):
            c_x = (x - width / 2) * 4 / width
            color_value = mandelbrot(complex(c_x,c_y), max_iter)
            if color_value < max_iter:
                color_value = (0, 0, 0)
            else:
                color_value = ((color_value + color) % 255, (color_value * 2 + color) % 255, (color_value * 3 + color) % 255)
            result.extend(color_value)
if along_x:
    vertical()
else:
    horizontal()
client_socket.sendall(result)
client_socket.close()
