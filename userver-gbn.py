from socket import *

from threading import Thread


serverPort = 12000

serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))

print('The server is ready to receive')

rcv_base = 0  # next sequence number we wait for


queueing_delay = 500000

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

    def ack(self):
        seq_n = int(self.message.decode())
        global queue_size
        global program_over
        global system_time
        queue_size -= 1
        print("Seq n : %d, Queue Items : %d" % (seq_n, queue_size))
        if seq_n >= 999 and queue_size < 1:
            program_over = True
        if self.next is not None:
            self.next.arrival_time = system_time
        print("Restored From Queue, Arrival At %d, now %d" % (self.arrival_time, system_time))
        serverSocket.sendto(str(seq_n).encode(), self.clientAddress)
        return self.next

    def passed_queue(self):
        global system_time
        global queueing_delay
        return system_time - self.arrival_time >= queueing_delay







def queue_manager():
    global system_time
    global queue_head
    global program_over
    while not program_over:

        system_time += 1
        if queue_head is not None:
            if queue_head.passed_queue():
                queue_head = queue_head.ack()



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



