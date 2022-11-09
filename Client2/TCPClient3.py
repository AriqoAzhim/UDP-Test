# Author: Muhammad Ariq Al azhim, adapted from TCPClient3.py by Wei Song (Tutor for COMP3331/9331)

from socket import *
import sys
from getpass import getpass
import time
import os
import select
import threading

from functionalities import *
import presenter
import audience

def auth():
    username = input("Username: ")
    message = username
    clientSocket.sendall(message.encode())

    password = getpass("Password: ")
    message = password
    clientSocket.sendall(message.encode())
    return username

def UDP_listener():
    # create thread for UDP, keep listening for packages and receive them
    sockName = clientSocket.getsockname()
    timeout = 3
    UDP_Audience = threading.Thread(target=audience.receive_file, args=(sockName[0], sockName[1], timeout))
    UDP_Audience.daemon = True
    UDP_Audience.start()

if __name__ == "__main__":

    # check that arguments 
    if len(sys.argv) != 3:
        print("\n===== Error usage, python3 TCPClient3.py SERVER_IP SERVER_PORT ======\n")
        exit(0)
    serverHost = sys.argv[1]
    serverPort = int(sys.argv[2])
    serverAddress = (serverHost, serverPort)
    edgeDeviceName = None

    # define a socket for the client side, it would be used to communicate with the server
    clientSocket = socket(AF_INET, SOCK_STREAM)

    # build connection with the server and send message to it
    clientSocket.connect(serverAddress)

    # Trigger Authentication
    authFlag = False
    while authFlag == False:
        data = clientSocket.recv(1024)
        receivedMessage = data.decode()

        # parse the message received from server and take corresponding actions
        if receivedMessage == "":
            print("[recv] Message from server is empty!")
        elif receivedMessage == "authentication":
            edgeDeviceName = auth()
            continue
        elif receivedMessage == "retry auth":
            print("Invalid Password. Please try again")
            edgeDeviceName = auth()
            continue
        elif receivedMessage == "success auth":
            print("Welcome!")
            authFlag = True
        elif receivedMessage == "failed auth":
            print(
                "Connection with this user has been blocked, please wait and try again later"
            )

    # initialise Audience Component
    UDP_listener()
    
    while True:
        message = input(
            "Enter one of the following commands (EDG, UED, SCS, DTE, AED, OUT): "
        )
        args = message.split(" ")
        command = args[0]

        match command:
            case "EDG":
                EDG(edgeDeviceName, args)
            case "UED":
                UED(edgeDeviceName, clientSocket, args)
            case "SCS":
                SCS(edgeDeviceName, clientSocket, args)
            case "DTE":
                DTE(edgeDeviceName, clientSocket, args)
            case "AED":
                AED(clientSocket)
            case "OUT":
                if OUT(clientSocket, message):
                    break
            case "UVF":
                UVF(args)
            case _:
                print("Invalid Command: " + "\"" + message + "\"")
                continue

    # close the socket
    print("closing socket")
    clientSocket.close()

