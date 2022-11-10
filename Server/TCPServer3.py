# Author: Muhammad Ariq Al azhim, adapted from TCPServer3.py by Wei Song (Tutor for COMP3331/9331)

from socket import *
from threading import Thread
import sys
import time
from datetime import datetime
import os
import serverLogging as log

global blackList
blackList = {}
# global loginAttempts
# loginAttempts = {}

# when a user is added to the blackList, they are initialised with a value of 10
# every second, reduce value by one. If val = 0, remove them from the blacklist
def blackList_timer():
    while True:
        toBeRemoved = []
        for item in blackList.items():
            if item[1] != 0:
                blackList[item[0]] = item[1] - 1
            else:
                toBeRemoved.append(item[0])

        for x in toBeRemoved:
            blackList.pop(x, 0)
        time.sleep(1)


# Sequence Number Initialised
global AEDSeqNum
AEDSeqNum = 1


def iterate_AEDSeqNum():
    global AEDSeqNum
    AEDSeqNum += 1


def decrement_AEDSeqNum():
    global AEDSeqNum
    AEDSeqNum -= 1


def add_auth_attempt(username, loginAttempts):
    # if no logins have been attempted yt
    if len(loginAttempts) == 0:
        loginAttempts[username] = 1
    else:
        for item in loginAttempts.items():
            if item[0] == username:
                loginAttempts[item[0]] = item[1] + 1
                return
        loginAttempts[username] = 1


def clear_login_attempts(username, loginAttempts):
    loginAttempts.pop(username)


def get_auth_attempts(username, loginAttempts):
    for item in loginAttempts.items():
        if item[0] == username:
            return item[1]


def auth_user(credentials, username, password):
    try:
        if credentials[username] == password:
            return True
        # if password is wrong
        else:
            return False
    # if the password doesnt exist
    except:
        return False


# check if file exists -> Boolean
def check_file_exists(filename):
    if os.path.isfile(filename) != True:
        print(f"{filename} does not exist")
        return False
    else:
        return True


# give current timestamp -> string
def curr_timestamp():
    now = datetime.now()
    return now.strftime("%d %B %Y %H:%M:%S")


# process computation given a filename -> string, float
def process_computation(edgeDeviceName, computation, filename):
    num_list = []
    with open(filename) as f:
        lines = f.readlines()
        for i in lines[:-1]:
            num_list.append(int(i[:-1]))
        num_list.append(int(lines[-1]))

    print(
        f"{computation} computation has been made on edge device {edgeDeviceName}, for data file {filename}, the result is: "
    )
    match computation:
        case "SUM":
            result = sum(num_list)
            return result
        case "AVERAGE":
            result = sum(num_list) / len(num_list)
            return result
        case "MAX":
            return max(num_list)
        case "MIN":
            return min(num_list)


# checks for amount of data/lines in a given file
def file_data_amount(filename):
    with open(filename, "r") as f:
        for count, line in enumerate(f):
            pass
        return count + 1


# returns all other Active Edge Devices apart from the given one -> string
def process_AED(edgeDeviceName, client):
    AEDList = ""
    with open("edge-device-log.txt") as f:
        lines = f.readlines()
        for line in lines:
            lineList = line.split("; ")
            if lineList[2] == edgeDeviceName:
                continue
            else:
                AEDList = (
                    AEDList
                    + f"{lineList[2]} active since {lineList[1]}, IP Address: {client.clientAddress[0]} Port: {str(client.clientAddress[1])} \n"
                )
    return AEDList


def get_IP_Port(edgeDeviceName):
    output = []
    with open("edge-device-log.txt") as f:
        lines = f.readlines()
        for line in lines:
            lineList = line.split("; ")
            if lineList[2] == edgeDeviceName:
                # append ip address
                output.append(str(lineList[3]))
                # append port num
                output.append(str(lineList[4]))
    return output


class ClientThread(Thread):
    def __init__(self, clientAddress, clientSocket):
        Thread.__init__(self)
        self.clientAddress = clientAddress
        self.clientSocket = clientSocket
        self.clientAlive = False
        self.clientAuth = False
        self.clientName = None
        self.clientLoginAttempts = {}

        print("===== New connection created for: ", clientAddress)
        self.clientAlive = True

    def run(self):
        # get list of authenticated users
        usernames_pass = {}
        # process the list of users able to use server
        for i in open("credentials.txt"):
            x = i.split(" ", 1)
            usernames_pass[x[0]] = x[1][:-1]

        message = ""
        while self.clientAlive:
            # Authentication Loop
            while self.clientAuth == False:

                # if there have been login Attempts
                if len(self.clientLoginAttempts) > 0:
                    message = "retry auth"
                else:
                    message = "authentication"
                self.clientSocket.send(message.encode())

                # get username and password from client
                data = self.clientSocket.recv(1024)
                username = data.decode()
                data = self.clientSocket.recv(1024)
                password = data.decode()

                # if user is in the blacklist do not attempt authentication
                if username in blackList:
                    print(f"User {username} is currently blocked from authenticating")
                    print(f"Please wait {blackList[username]} seconds before retrying")

                    message = "failed auth"
                    self.clientSocket.send(message.encode())
                    continue

                # attempt authentication, True if valid, False if not
                self.clientAuth = auth_user(usernames_pass, username, password)

                # +1 to login attempt for the specified user
                add_auth_attempt(username, self.clientLoginAttempts)

                # if num attempts = max number of attempts, block user for 10 seconds
                if get_auth_attempts(username, self.clientLoginAttempts) == attempts:
                    message = "failed auth"
                    self.clientSocket.send(message.encode())
                    print(f"Blocking Authentication with {username} for 10 seconds")

                    blackList[username] = 10
                    # after a block, clear the login attempts
                    self.clientLoginAttempts.clear()
                    continue

                # if outcome of authentication was True, go into command loop
                if self.clientAuth == True:
                    message = "success auth"
                    self.clientSocket.send(message.encode())
                    self.clientName = username

                    logMessage = f"{AEDSeqNum}; {curr_timestamp()}; {self.clientName}; {self.clientAddress[0]}; {str(self.clientAddress[1])}; "

                    log.edge_device_connection_log(logMessage)

                    print(f"{self.clientAddress} authenticated!")
                    iterate_AEDSeqNum()

            # use recv() to receive message from the client
            data = self.clientSocket.recv(1024)
            message = data.decode()
            message = message.strip()
            out = message.split(" ")

            command = out[0]
            match command:
                case "EDG":
                    print(f"Edge Device {self.clientName} issued command EDG")
                case "UED":
                    print(f"Edge Device {self.clientName} issued command UED")

                    # send ACK of UED data transfer
                    message = "UED ACK"
                    self.clientSocket.send(message.encode())
                    filename = out[1].split("-")

                    print(f"A data file is received from edge device {self.clientName}")
                    with open(out[1] + ".txt", "w") as f:
                        f.write(out[3])

                    # log data transfer
                    logMessage = (
                        f"{filename[0]}; {curr_timestamp()}; {filename[1]}; {out[2]};"
                    )
                    log.log(logMessage)
                    print("upload_log.txt has been updated")
                case "SCS":
                    print(
                        f"Edge Device {self.clientName} requested a computation operation of {out[1]} for {out[2]}"
                    )
                    if check_file_exists(out[2]) != True:
                        self.clientSocket.send("file does not exist".encode())
                        continue

                    result = str(process_computation(self.clientName, out[1], out[2]))
                    print(result)
                    self.clientSocket.send(result.encode())
                case "DTE":
                    print(f"Edge Device {self.clientName} issued command DTE")
                    filename = out[1]
                    if check_file_exists(filename) != True:
                        self.clientSocket.send("file does not exist".encode())
                        continue
                    dataAmount = file_data_amount(filename)
                    os.remove(filename)
                    now = datetime.now()
                    timestamp = now.strftime("%d %B %Y %H:%M:%S")

                    filelist = filename.split("-")
                    edgeDeviceName = filelist[0]
                    fileID = filelist[1][:-4]

                    log.delete_log(
                        f"{edgeDeviceName}; {timestamp}; {fileID}; {dataAmount}"
                    )

                    message = "DTE success"
                    self.clientSocket.send(message.encode())
                case "AED":
                    print(f"Edge Device {self.clientName} issued command AED")
                    AED = process_AED(self.clientName, self)
                    if AED == "":
                        message = "There are no other devices active"
                    else:
                        message = AED

                    print(f"message = {message}")
                    self.clientSocket.send(message.encode())

                case "OUT":
                    print(f"{self.clientName} exited the edge network")
                    self.clientAlive = False

                    decrement_AEDSeqNum()
                    log.update_edge_device_log(self.clientName)
                case "":
                    self.clientAlive = False
                    print("===== the user disconnected - ", self.clientAddress)
                    break
                # return if given device is active -> True/False
                case "status":
                    print(out)
                    checkDevName = out[1]
                    print(checkDevName)
                    activeStatus = int(log.get_edge_device_seq_num(checkDevName))
                    print(f"active status : + {activeStatus}")
                    # if not active, return 0
                    if activeStatus == 0:
                        message = str(activeStatus)
                        self.clientSocket.send(message.encode())
                        continue

                    IPPortList = get_IP_Port(checkDevName)
                    # return IP and Port of the checked Device
                    message = f"{IPPortList[0]} {IPPortList[1]}"
                    self.clientSocket.send(message.encode())
                case _:
                    print(out)
                    print("[send] Cannot understand this message")
                    message = "Cannot understand this message"
                    self.clientSocket.send(message.encode())


if __name__ == "__main__":
    # acquire server host and port from command line parameter
    if len(sys.argv) != 3:
        print(
            "\n===== Error usage, python3 TCPServer3.py SERVER_PORT maxServerAuthAttempts ======\n"
        )
        exit(0)
    # check if valid value for maxServerAuthAttempts was given
    try:
        attempts = int(sys.argv[2])
        if attempts < 1 or attempts > 5:
            raise Exception
    except:
        print("valid value of argument number is an integer between 1 and 5")
        exit(0)

    # remove previous AED log file if it exists
    if check_file_exists("edge-device-log.txt"):
        os.remove("edge-device-log.txt")

    # initalise server parameters
    serverHost = "127.0.0.1"
    serverPort = int(sys.argv[1])
    serverAddress = (serverHost, serverPort)

    # define socket for the server side and bind address
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(serverAddress)

    # create thread for auth blacklist
    auth_blacklist_timer = Thread(target=blackList_timer)
    auth_blacklist_timer.daemon = True
    auth_blacklist_timer.start()

    # start listening for clients and generate client threads if detected
    while True:
        serverSocket.listen()
        clientSockt, clientAddress = serverSocket.accept()
        clientThread = ClientThread(clientAddress, clientSockt)
        clientThread.start()
