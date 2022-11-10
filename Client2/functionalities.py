import os
import presenter

# check if file exists -> Boolean
def check_file_exists(filename):
    if os.path.isfile(filename) != True:
        print(f"{filename} does not exist")
        return False
    else:
        return True


# checks for amount of data/lines in a given file
def file_data_amount(filename):
    with open(filename, "r") as f:
        for count, line in enumerate(f):
            pass
        return count + 1


def EDG(edgeDeviceName, args):
    # Generate Edge Device Data
    if len(args) != 3:
        print("Invalid input: EDG <fileID> <DataSampleNum>")
        return False

    try:
        fileID = int(args[1])
        dataSampleNum = int(args[2])
    except:
        print(
            "the fileID or dataAmount are not integers, you need to specify the parameter as integers"
        )
        return False

    # remove previous AED log file if it exists
    filename = f"{edgeDeviceName}-{fileID}.txt"
    if check_file_exists(filename):
        os.remove(filename)
    with open(filename, "w+") as f:
        counter = 0
        while counter < dataSampleNum:
            counter += 1
            f.write(f"{counter}\n")

    print("Data Generation Done!")
    return True


def UED(edgeDeviceName, client, args):
    # Generate Edge Device Data
    if len(args) != 2:
        print("Invalid input: UED <fileID>")
        return False

    try:
        fileID = int(args[1])
    except:
        print("the fileID is not an integer, you need to it as an integer")
        return False

    filename = f"{edgeDeviceName}-{fileID}.txt"
    if not check_file_exists(filename):
        return False

    with open(f"{edgeDeviceName}-{fileID}.txt", "r") as f:
        dataToSend = f.read()

    dataAmount = file_data_amount(filename)
    message = "UED " + filename[:-4] + " " + str(dataAmount) + " " + dataToSend
    client.sendall(message.encode())

    data = client.recv(1024)
    receivedMessage = data.decode()

    if receivedMessage == "UED ACK":
        print(f"Data file with ID of {fileID} has been uploaded to Server")
    else:
        print("Transfer Failed")
        return False

    return True


def prep_computation(edgeDeviceName, client, computation, fileID):
    message = f"SCS {computation} " + f"{edgeDeviceName}-{fileID}.txt"
    client.sendall(message.encode())

    data = client.recv(1024)
    receivedMessage = data.decode()

    if receivedMessage == "file does not exist":
        print("File does not exist on the server side")
        return False
    else:
        print(f"{computation} = " + receivedMessage)
        return True


def SCS(edgeDeviceName, client, args):
    if len(args) != 3:
        print("Invalid input: SCS <fileID> <computationOperation>")
        return False

    try:
        fileID = int(args[1])
    except:
        print("the fileID is not an integer")
        return False

    computation = args[2]
    if computation == "SUM" or "AVERAGE" or "MAX" or "MIN":
        if prep_computation(edgeDeviceName, client, computation, fileID) != True:
            return False
    else:
        print("invalid computation, try again")
        return False


def DTE(edgeDeviceName, client, args):
    if len(args) != 2:
        print("Invalid input: DTE <fileID>")
        return False

    try:
        fileID = int(args[1])
    except:
        print("the fileID is not an integer")
        return False

    message = "DTE " + f"{edgeDeviceName}-{fileID}.txt"
    client.sendall(message.encode())

    data = client.recv(1024)
    receivedMessage = data.decode()

    if receivedMessage == "file does not exist":
        print("File does not exist on the server side")
    else:
        print(f"File with fileID {fileID} successfully removed from the central server")


def AED(client):
    client.sendall("AED".encode())

    data = client.recv(1024)
    receivedMessage = data.decode()

    print("received message = " + receivedMessage)


def OUT(edgeDeviceName, client, message):
    print(f"Bye, {edgeDeviceName}!")
    client.sendall(message.encode())
    return True


def UVF(client, args):
    if len(args) != 3:
        print("Invalid input: UVF <deviceName> <filename>")
        return False

    # this device is the presenter and the target is the audience
    filename = args[2]

    if not check_file_exists(filename):
        return False

    deviceName = str(args[1])
    # check if device is active, if not send error message
    message = f"status {deviceName}"
    client.sendall(message.encode())

    data = client.recv(1024)
    receivedMessage = data.decode()

    if receivedMessage == "0":
        print(f"Device {deviceName} is inactive")
        return False
    else:
        print(f"Attempting to send file to {args[1]}")

    toIP, toPort = receivedMessage.split()

    try:
        presenter.present_file(toIP, int(toPort), filename, deviceName)
    except:
        print(f"unable to present {filename} to {deviceName}")
