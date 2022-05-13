from socket import *
import time

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
filename = 'message.txt'

with open(filename, 'r') as file:
    while True:
        # check timeout here and break

        packet = filename.read(PACKET_SIZE)
        client_socket.sendto(packet.encode(),(IP_ADDRESS, RECEIVING_PORT))