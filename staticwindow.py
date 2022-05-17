# Importing the required libraries
import socket
import re
import sys


# Defining Global Parameters
# IP address of the receiver. "" implies localhost
IP_ADDRESS = ""
# Port number on localhost on which receiver runs
PORT = int(input("Enter the Port number you want your sender to run: "))
# Size of the buffer, defining the maximum data that can be buffered for transmission at a time
PACKET_SIZE = 1000
# Number of Packets in Window
WINDOW_SIZE = 5
#Acknowledged Packets
ack_sequences = [0]
data_packets = ["first dummy entry"]
x = 0
file_name = "message.txt"
packet_num = 0
prev_ack = -1
ack_num = -1
curr_ack = -1
base = 1
next_seq_num = 1
socket.setdefaulttimeout(5)

# Instatiating a UDP Socket
sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


#general process: read data from file, add delim to the beginning of the data, to form packet,
# send packet with header delim and data. Send window size number of packets, and wait for ack 
# for each of these packets. If we get a timeout or we get duplicate acks
#  then we know we have lost a packet, and need to resend packet ack# - 1 

f = open(file_name, "rb") #open file

x = 0
while(True):
    #x += 1
    #send packet to receiver
    #check if next packet to be sent is in the window
    if(next_seq_num >= base and next_seq_num <= (base + WINDOW_SIZE - 1)): 
        data = f.read(PACKET_SIZE) # read 1000 bytes from file
        if(len(data) == 0): break # if were done reading data then break out of the loop
        data_str = data.decode() # convert to string so we can add header
        print("data size:", len(data))
        if(len(data) < 300): 
            print("data:",data)
            #break
        delim = str(next_seq_num) + '|'
        data_str = delim + data_str  
        data_packets.append(data_str) #store after we add the header
        #print("data str:", data_str)
        print("sending packet:", next_seq_num)
        sender_socket.sendto(data_str.encode(), (IP_ADDRESS, PORT))
        next_seq_num = next_seq_num + 1
        continue
        #receiver acknowledgement
    try:
        prev_ack = ack_num 
        ack_num,addr = sender_socket.recvfrom(4)  
        #curr_ack = ack_num
        if(ack_num == prev_ack): #Check for same ack number back to back
            sender_socket.sendto(data_packets[ack_num + 1].encode(), (IP_ADDRESS, PORT))
        #print("ack size:", len(ack_num))
        #print("got ack for packet:", ack_num.decode())

        #When we get an acknowledgement, we know all packets up to that number have been acknowledged
        #so we can make the base that acknowledgement
        base = int(ack_num)
        continue
    except socket.timeout:
        print("had a timeout")
        sender_socket.sendto(data_packets[ack_num + 1].encode(), (IP_ADDRESS, PORT))
        break

sender_socket.close()