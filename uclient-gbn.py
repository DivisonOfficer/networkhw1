from socket import *
from threading import Thread
import random
import time

serverIP = '127.0.0.1' # special IP for local host
serverPort = 12000
clientPort = 12001

win = 10.0      # window size
max_win_size = 0
avg_win_size = 0
timeout_interval = 10 # timeout interval


#const
no_pkt = 10000 # the total number of packets to send
send_base = 0 # oldest packet sent
loss_rate = 0.01 # loss rate
expire_count_max = 100000


seq = 0        # initial sequence number
timeout_flag = 0 # timeout trigger

expire_count = 0


global_rtt = 0

timeout_cnt = 0

sent_time = [0 for i in range(no_pkt * 2)]


clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.bind(('', clientPort))
clientSocket.setblocking(0)

# thread for receiving and handling acks

def onAfterTimeOut():

    global win
    if win > 2 :
        win = win / 2

    return

def winSlowStartStep(seq):
    global win
    global avg_win_size
    global max_win_size
    win = win + 1 / win

    if win > max_win_size:
        max_win_size = win

    avg_win_size = avg_win_size + (win - avg_win_size) / (seq + 1)


def printSeqWithStatus(seq):
    global win
    global timeout_interval
    if seq % 10 != 0 :
        return
    print("SEQ %4d | WIN %3d | TO ITV %5f" % (seq, win, timeout_interval))
def handling_ack():
    print("thread")
    global clientSocket
    global send_base
    global timeout_flag
    global sent_time

    alpha = 0.125
    beta = 0.25
    global timeout_interval # timeout interval


    pkt_delay = 0
    dev_rtt = 0
    init_rtt_flag = 1

    while True:

        if sent_time[send_base] != 0:
            pkt_delay = time.time() - sent_time[send_base]


        if pkt_delay > timeout_interval and timeout_flag == 0:    # timeout detected

            global timeout_cnt
            timeout_cnt += 1

            print("timeout detected:", str(send_base), flush=True)
            print("timeout interval:", str(timeout_interval), flush=True)

            print("timeout ratio : %f" % (timeout_cnt/ seq))
            timeout_flag = 1

            onAfterTimeOut()
        global expire_count
        global expire_count_max
        try:
            ack, serverAddress = clientSocket.recvfrom(2048)
            ack_n = int(ack.decode())
            printSeqWithStatus(ack_n)

            if init_rtt_flag == 1:
                estimated_rtt = pkt_delay
                init_rtt_flag = 0
            else:
                estimated_rtt = (1-alpha) * estimated_rtt + alpha*pkt_delay
                dev_rtt = (1-beta)*dev_rtt + beta*abs(pkt_delay-estimated_rtt)
            expire_count = 0
            winSlowStartStep(ack_n)

            global global_rtt
            global_rtt = estimated_rtt

            timeout_interval = estimated_rtt + 4*dev_rtt
            #print("timeout interval:", str(timeout_interval), flush=True)


        except BlockingIOError:
            expire_count += 1

            if expire_count > expire_count_max:
                return

            continue

        # window is moved upon receiving a new ack
        # window stays for cumulative ack
        send_base = ack_n + 1

        if ack_n == no_pkt - 1:
            break;

# running a thread for receiving and handling acks
th_handling_ack = Thread(target = handling_ack, args = ())
th_handling_ack.start()

while seq < no_pkt:
    while seq < send_base + win: # send packets within window
        if random.random() < 1 - loss_rate: # emulate packet loss
            clientSocket.sendto(str(seq).encode(), (serverIP, serverPort))
        sent_time[seq] = time.time()
        seq = seq + 1

    if timeout_flag == 1: # retransmission
        seq = send_base
        clientSocket.sendto(str(seq).encode(), (serverIP, serverPort))
        sent_time[seq] = time.time()
        print("retransmission:", str(seq), flush=True)
        seq = seq + 1
        timeout_flag = 0


th_handling_ack.join() # terminating thread




print ("done")
print ("Mean RTT : %f" % global_rtt)
print ("MAX WIN SIZE : %d \nAVG WIN SIZE : %2f" % (max_win_size, avg_win_size))

clientSocket.close()


