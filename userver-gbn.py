from socket import *

from threading import Thread

from time import sleep


#const

serverPort = 12000
max_packet_num = 10000
queueing_delay = 0.003

serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))

print('The server is ready to receive')

rcv_base = 0  # next sequence number we wait for



last_success_seq = -1
success_seq_dict = dict()

queue_maxsize = 10

system_time = 0

queue_head = None
queue_tail = None
queue_size = 0

program_over = False



class QueueItem:

    def __init__(self, message, clientAddress):
        self.next = None
        self.message = message
        self.clientAddress = clientAddress
        global system_time
        self.arrival_time = system_time

#큐의 첫번째 아이템을 잘 수신했다는 ACK를 반환합니다.
    def ack(self):
        seq_n = int(self.message.decode())
        global queue_size
        global program_over
        global system_time
        global max_packet_num
        global last_success_seq
        global success_seq_dict


        # 연속된 가장 마지막의 seq 번호를 보내도록 합니다.
        if last_success_seq < seq_n:
            success_seq_dict[seq_n] = 1
            success_seq = seq_n
            success_until = True
            while success_seq > last_success_seq:
                if success_seq not in success_seq_dict:
                    success_until = False
                    break
                success_seq -= 1

            if success_until:
                while last_success_seq < seq_n:
                    if last_success_seq in success_seq_dict:
                        del success_seq_dict[last_success_seq]
                    last_success_seq += 1



        queue_size -= 1

        print("Seq n : %d, Queue Items : %d" % (seq_n, queue_size))
        #if seq_n >= max_packet_num - 1 and queue_size < 1:
        #    program_over = True

        if self.next is not None:
            self.next.arrival_time = system_time
        #print("Restored From Queue, Arrival At %d, now %d" % (self.arrival_time, system_time))
        serverSocket.sendto(str(last_success_seq).encode(), self.clientAddress)
        return self.next

    def passed_queue(self):
        global system_time
        global queueing_delay
        return True
    #system_time - self.arrival_time >= queueing_delay






# 새로은 쓰레드를 만들어서 큐를 읽습니다. 큐 딜레이 구현을 위해, 한번 큐를 읽고 나면 대기 시간을 가집니다.
def queue_manager():
    global system_time
    global queue_head
    global program_over
    global queueing_delay
    while not program_over:

        system_time += 1
        if queue_head is not None:
            if queue_head.passed_queue():
                queue_head = queue_head.ack()

        sleep(queueing_delay)



th_queue = Thread(target = queue_manager, args = ())
th_queue.start()



def put_in_queue(message, clientAddress):
    global queue_size
    global queue_head
    global queue_tail
    if queue_size >= queue_maxsize:
        return

    item = QueueItem(message, clientAddress)

    if queue_head == None:
        queue_head = item
        queue_tail = item
    else :
        queue_tail.next = item
        queue_tail = item

    queue_size += 1





while program_over == False:
    message, clientAddress = serverSocket.recvfrom(2048)
    seq_n = int(message.decode()) # extract sequence number
    #print(seq_n)

    put_in_queue(message, clientAddress)

    #if seq_n == rcv_base: # in order delivery
    #    rcv_base = seq_n + 1
    #serverSocket.sendto(str(rcv_base-1).encode(), clientAddress) # send cumulative ack
    #if seq_n == 999:
    #    break;

serverSocket.close()



