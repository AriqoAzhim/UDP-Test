# Author: Muhammad Ariq Al azhim, adapted from TCPServer3.py by Wei Song (Tutor for COMP3331/9331)
from socket import *
import sys
from getpass import getpass
import time
import os
import presenter
import audience
import select
import threading

def auth():
    username = input("Username: ")
    message = username
    clientSocket.sendall(message.encode())

    password = getpass("Password: ")
    message = password
    clientSocket.sendall(message.encode())
    return username

# check if file exists -> Boolean
def check_file_exists(filename):
    print(os.path.isfile(filename))
    if os.path.isfile(os.path.join(os.getcwd(), filename)) != True:
        print(f"{filename} does not exist")
        return False
    else:
        return True

def fileDataAmount(filename):
    with open(filename, 'r')  as f:
        for count, line in enumerate(f):
            pass
        return count + 1

def prep_computation(computation):
    message = f"SCS {computation} " + f"{edgeDeviceName}-{fileID}.txt"
    clientSocket.sendall(message.encode())

    data = clientSocket.recv(1024)
    receivedMessage = data.decode()

    if receivedMessage == "file does not exist":
        print("File does not exist on the server side")
        return False
    else:
        print(f"{computation} = " + receivedMessage)
        return True

# Server would be running on the same host as Client
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

authFlag = False

while authFlag == False:
    # receive response from the server
    # 1024 is a suggested packet size, you can specify it as 2048 or others
    # receive auth message
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
            "Too many login attempts, try again later, Connection will close in 10 seconds"
        )
        time.sleep(10)
        exit(0)
    else:
        wait = input("case not accounted for lol")

# create thread for UDP, keep listening for packages and receive them
sockName = clientSocket.getsockname()
timeout = 3
UDP_Audience = threading.Thread(target=audience.receive_file, args=(sockName[0], sockName[1], timeout))
UDP_Audience.daemon = True
UDP_Audience.start()

while True:
    message = input(
        "Enter one of the following commands (EDG, UED, SCS, DTE, AED, OUT): "
    )
    message = message.strip()
    out = message.split(" ")
    command = out[0]

    match command:
        case "EDG":
            # Generate Edge Device Data
            if len(out) != 3:
                print("Invalid input: EDG <fileID> <DataSampleNum>")
                continue

            try:
                fileID = int(out[1])
                dataSampleNum = int(out[2])
            except:
                print(
                    "the fileID or dataAmount are not integers, you need to specify the parameter as integers"
                )
                continue

            filename = f"{edgeDeviceName}-{fileID}.txt"

            # remove previous AED log file if it exists
            if check_file_exists(filename):
                os.remove(filename)
            with open(filename, "w+") as f:
                counter = 0
                while counter < dataSampleNum:
                    counter += 1
                    f.write(f"{counter}\n")

            print("Data Generation Done!")

        case "UED":
            # Generate Edge Device Data
            if len(out) != 2:
                print("Invalid input: UED <fileID>")
                continue

            try:
                fileID = int(out[1])
            except:
                print(
                    "the fileID is not an integer, you need to it as an integer"
                )
                continue

            file = f"{edgeDeviceName}-{fileID}.txt"
            if os.path.isfile(file) != True:
                print(f"{file} does not exist")
                continue
            with open(f"{edgeDeviceName}-{fileID}.txt", "r") as f:
                dataToSend = f.read()
            
            dataAmount = fileDataAmount(file)
            message = "UED " + file[:-4] + " " + str(dataAmount) + " " + dataToSend
            clientSocket.sendall(message.encode())

            data = clientSocket.recv(1024)
            receivedMessage = data.decode()

            if receivedMessage == "UED ACK":
                print("Transfer Success")
            else:
                print("Transfer Failed")
                continue
        case "SCS":
            # SCS fileID computationOperation
            # SUM , AVERAGE, MIN, SUM of a file
                        # Generate Edge Device Data
            if len(out) != 3:
                print("Invalid input: SCS <fileID> <computationOperation>")
                continue

            try:
                fileID = int(out[1])
            except:
                print(
                    "the fileID is not an integer"
                )
                continue

            computation = out[2]
            if computation == "SUM" or "AVERAGE" or "MAX" or "MIN":
                if prep_computation(computation) != True:
                    continue
            else:
                print("invalid computation, try again")
                continue

        case "DTE":
            if len(out) != 2:
                print("Invalid input: DTE <fileID>")
                continue

            try:
                fileID = int(out[1])
            except:
                print(
                    "the fileID is not an integer"
                )
                continue
            message = "DTE " + f"{edgeDeviceName}-{fileID}.txt"
            clientSocket.sendall(message.encode())

            data = clientSocket.recv(1024)
            receivedMessage = data.decode()

            if receivedMessage == "file does not exist":
                print("File does not exist on the server side")
            else:
                print(f"File with fileID {fileID} successfully removed from the central server")

        case "AED":
            clientSocket.sendall("AED".encode())

            data = clientSocket.recv(1024)
            receivedMessage = data.decode()
            
            print("received message = " + receivedMessage)
        case "OUT":
            print("Good Bye")
            clientSocket.sendall(message.encode())

            data = clientSocket.recv(1024)
            receivedMessage = data.decode()
            break
        case "UVF":
            if len(out) != 3:
                print("Invalid input: UVF <deviceName> <filename>")
                continue

            # this device is the presenter and the target is the audience
            filename = out[2]
            
            if not check_file_exists(filename):
                break

            deviceName = out[1]
            # check if device is active, if not send error message
            message = f"status {deviceName}"
            clientSocket.sendall(message.encode())

            data = clientSocket.recv(1024)
            receivedMessage = data.decode()

            if receivedMessage == "0":
                print(f"Device {deviceName} is inactive")
            else:
                print(f"Attempting to send file to {out[1]}")
            
            toIP, toPort = receivedMessage.split()

            try:
                presenter.present_file(toIP, int(toPort), filename, deviceName)
            except:
                print(f"unable to present {filename} to {deviceName}")
        case _:
            print(out)

# close the socket
print("closing socket")
clientSocket.close()
