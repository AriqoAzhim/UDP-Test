import os


def log(message):
    with open("log.txt", "a") as logs:
        logs.write(message + "\n")


def delete_log(message):
    with open("deletion-log.txt", "a") as logs:
        logs.write(message + "\n")


def edge_device_connection_log(message):
    with open("edge-device-log.txt", "a") as logs:
        logs.write(message + "\n")


def get_edge_device_seq_num(edgeDeviceName):
    print(f"finding seqNum of {edgeDeviceName}")

    with open("edge-device-log.txt") as f:
        lines = f.readlines()
        print(lines)
        for line in lines:
            lineList = line.split("; ")
            if lineList[2] == edgeDeviceName:
                return int(lineList[0])
    return 0


def update_edge_device_log(edgeDeviceName):
    with open("edge-device-log.txt", "r+") as f:
        lines = f.readlines()
        x = get_edge_device_seq_num(edgeDeviceName)
        updatedLines = []
        for i in lines[x:]:
            currLine = i.split("; ")
            updatedVal = int(currLine[0]) - 1
            currLine[0] = updatedVal
            updatedLine = f"{currLine[0]}; {currLine[1]}; {currLine[2]}; {currLine[3]}; {currLine[4]}; \n"
            updatedLines.append(updatedLine)
        newLines = lines[: x - 1] + updatedLines

    os.remove("edge-device-log.txt")

    with open("edge-device-log.txt", "w+") as f:
        for line in newLines:
            f.write(line)
