# Presents files

from socket import *
import time
import sys


def present_file(IP, Port, filename, toEdgeDevice):
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.sendto(filename.encode(), (IP, Port))
    print(f"Attempting to send {filename} to {toEdgeDevice}")

    with open(filename, "rb") as f:
        data = f.read(1024)
        while data:
            if sock.sendto(data, (IP, Port)):
                data = f.read(1024)
                time.sleep(0.02)
