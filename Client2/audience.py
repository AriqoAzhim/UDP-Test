# Listens for File transfers

from socket import *
import select

def receive_file(IP, Port, timeout):
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind((IP, Port))

    while True:
        data, addr = sock.recvfrom(1024)
        if data:
            filename = data.strip()
        with open(filename, 'wb') as f:
            while True:
                ready = select.select([sock], [], [], timeout)
                if ready[0]:
                    data, addr = sock.recvfrom(1024)
                    f.write(data)
                else:
                    print(f"\nFile {filename} successfuly transferred")
                    break