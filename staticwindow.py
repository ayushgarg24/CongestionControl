# Importing the required libraries
import socket
import re
import sys
import time
import math


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
dup_count = 0
file_name = "message.txt"
packet_num = 0
prev_ack = -1
ack_num = 0
curr_ack = -1
base = 1
next_seq_num = 1
temp_end = -1
delay_sum = 0
throughput_sum = 0
delays = [0]
throughputs = [0]
#initialize lists for tracking the timing
times = []
start = [0,0]
times.append(start)
socket.setdefaulttimeout(5)

# Instatiating a UDP Socket
sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def printInfo(base, seqSent, ackNum):
    currentWin = [base]
    for q in range(1,5):
        currentWin.append(base+q)
    print()
    print("Current Window:{}".format(currentWin))
    print("Sequence Number of Packet Sent:{}".format(seqSent))
    print("Acknowledgement Number Received:{}".format(ackNum))
    print()


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
        #print("data size:", len(data))
        #if(len(data) < 300): 
            #print("data:",data)
            #break
        delim = str(next_seq_num) + '|'
        data_str = delim + data_str  
        data_packets.append(data_str) #store packet after we add the header
        #print("sending packet:", next_seq_num)
        printInfo(base, next_seq_num, ack_num)
        start_time = time.time() #start time here
        sender_socket.sendto(data_str.encode(), (IP_ADDRESS, PORT))
        start = [start_time]
        times.append(start)
        next_seq_num = next_seq_num + 1
        continue
        #receiver acknowledgement
    try:
        prev_ack = ack_num 
        ack_num,addr = sender_socket.recvfrom(1024)  
        ack_num = int(ack_num)
        print("ack num:",ack_num)
        if(ack_num == prev_ack): #Check for same ack number back to back
            dup_count += 1
            if(dup_count >= 3):
                printInfo(base, ack_num + 1, ack_num)
                print("Thats a dupe^")
                sender_socket.sendto(data_packets[ack_num + 1].encode(), (IP_ADDRESS, PORT)) #resend packet
                dup_count = 0
            continue
        elif prev_ack > ack_num:
            print("got a dummy")
            ack_num = prev_ack
            #dup_count = 0
            continue
        else: #We know its not a duplicate ack, so save the end time
            #print("ack num:",ack_num)
            end_time = time.time()
            printInfo(base, next_seq_num-1, ack_num)
            print("Thats a normal ack^")
            times[ack_num].append(end_time)
            dup_count = 0
        #print("ack size:", len(ack_num))
        #print("got ack for packet:", ack_num.decode())

        #When we get an acknowledgement, we know all packets up to that number have been acknowledged
        #so we can make the base that acknowledgement
        if(ack_num != 0):
            base = int(ack_num) + 1
        #printInfo(base, next_seq_num-1, ack_num)
        continue
    except socket.timeout:
        print("had a timeout")
        sender_socket.sendto(data_packets[ack_num + 1].encode(), (IP_ADDRESS, PORT))
        break

#get the leftover acks
while(ack_num < next_seq_num - 1):
    try:
        prev_ack = ack_num 
        ack_num,addr = sender_socket.recvfrom(4)  
        ack_num = int(ack_num)
        if(ack_num == prev_ack): #Check for same ack number back to back
            dup_count += 1
            if(dup_count >= 3):
                printInfo(base, ack_num + 1, ack_num)
                print("Thats a dupe^")
                #resize window:
                window_size = 1
                sender_socket.sendto(data_packets[ack_num + 1].encode(), (IP_ADDRESS, PORT)) #resend packet
                dup_count = 0
            continue
        elif prev_ack > ack_num:
            print("got a dummy")
            ack_num = prev_ack
            dup_count = 0
            continue
        else: #We know its not a duplicate ack, so save the end time
            #print("ack num:",ack_num)
            dup_count = 0
            end_time = time.time()
            printInfo(base, next_seq_num-1, ack_num)
            print("Thats a normal ack^")
            times[ack_num].append(end_time)
        #print("ack size:", len(ack_num))
        #print("got ack for packet:", ack_num.decode())

        #When we get an acknowledgement, we know all packets up to that number have been acknowledged
        #so we can make the base that acknowledgement
        base = int(ack_num)
        continue
    except socket.timeout:
        print("had a timeout")
        sender_socket.sendto(data_packets[ack_num + 1].encode(), (IP_ADDRESS, PORT))
        dup_count = 0
        continue

#Add end times to the ones that dont have end times
for x in reversed(times):
    if(len(x) == 2):
        temp_end = x[1]
    else:
        x.append(temp_end)

#calculate avg delay throughput and performance
for x in times:
    delays.append(x[1] - x[0])

for x in delays:
    delay_sum += x
    if x != 0:
        throughputs.append((PACKET_SIZE + 2)/ x)

for x in throughputs:
    throughput_sum += x

avg_delay = (delay_sum / (len(delays) - 1)) * 1000 #avg delay in ms
avg_throughput = (throughput_sum / len(throughputs) - 1) * 8 #avg throughput in bits per second
performance = math.log10(avg_throughput) - math.log10(avg_delay)
print("Average Delay =", avg_delay, "ms")
print("Average Throughput =", avg_throughput, "bps")
print("Performance =", performance)
sender_socket.close()