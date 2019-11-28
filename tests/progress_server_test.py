import socket
import os

while True:
    ################################
    # Server for path, frame, bbox #
    ################################
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('localhost', 6367))
    print("binding...")

    data, addr = s.recvfrom(200)
    print(data)
