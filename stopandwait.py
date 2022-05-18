from socket import *
import time
import math

def printInformation(currentWin, seqSent, ackNum):
    print()
    print("Current Window: {}".format(currentWin))
    print("Seqeuence Number of Packet Sent: {}".format(seqSent))
    print("Acknowledgement Number Received: {}".format(ackNum))
    print()

    
# CONSTANTS
# IP address and port number
IP_ADDRESS = ""
RECEIVING_PORT = int(input("Enter the Port number the receiver is running on: "))

# Size of packet
PACKET_SIZE = 1000

# Timeout 
FIXED_TIMEOUT = 5

# sender socket
client_socket = socket(AF_INET, SOCK_DGRAM)
client_socket.settimeout(FIXED_TIMEOUT)
filename = 'message.txt'

transmitTimes = []
ackTimes = []

with open(filename, 'r') as file:
    seq_num = 1
    while True:
        packet = file.read(PACKET_SIZE)
        if not packet:
            break
        header = '{}|'.format(seq_num)
        packet = header + packet
        
        t0 = time.time()
        client_socket.sendto(packet.encode(),(IP_ADDRESS, RECEIVING_PORT))
        transmitTimes.append(t0)

        ACK = False
        while not ACK:
            try:
                response, address = client_socket.recvfrom(2048)
                ackTime = time.time()
                ACK = True
                ackNum = response.decode()
                ackTimes.append(ackTime)
                printInformation([seq_num], seq_num, ackNum)
                seq_num += 1
                
            except:
                client_socket.sendto(packet.encode(),(IP_ADDRESS, RECEIVING_PORT))
client_socket.close()
delayTimes = []
throughputs = []
for i in range(len(transmitTimes)):
    delay = ackTimes[i] - transmitTimes[i]
    throughput = 8*1002/delay
    delayTimes.append(delay)
    throughputs.append(throughput)

avgDelay = sum(delayTimes)/len(delayTimes) * 1000
avgThroughput = sum(throughputs)/len(throughputs)
Performance = math.log10(avgThroughput/avgDelay)

print("Average Delay = {}".format(avgDelay))
print("Average Throughput = {}".format(avgThroughput))
print("Performance = {}".format(Performance))