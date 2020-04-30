import sys
import threading
import datetime
from socket import (
    socket,
    AF_INET,
    SOCK_DGRAM
)

from packet import packet

WINDOW = 10
TIMEOUT = 0.1

class Sender():
    def __init__(self, emu_addr, emu_port, recv_port, in_file):
        # COMMAND LINE ARGS
        self.emu_addr = emu_addr
        self.emu_port = emu_port
        self.recv_port = recv_port
        self.in_file = in_file

        # SOCKETS
        self.recv_socket = socket(AF_INET, SOCK_DGRAM)
        self.recv_socket.bind(('', self.recv_port))
        self.out_socket = socket(AF_INET, SOCK_DGRAM)

        # PACKETS
        self.packets = self.file_to_packets()

        # SHARED VARIABLES
        self.base = 0
        self.acked_packets = 0
        self.last_acked = 0
        self.next_seq_num = 0
        self.timeout = False
        self.lock = threading.Lock()

        # TIMER
        self.timer = threading.Timer(TIMEOUT, self.has_timeout)
        self.start_time = 0

        # LOG FILES
        self.seq_num_log = open("seqnum.log", "w")
        self.ack_num_log = open("ack.log", "w")
        self.time_log = open("time.log", "w")

    # toggle timeout to true
    def has_timeout(self):
        self.lock.acquire()
        self.timeout = True
        self.lock.release()

    # convert input file to list of packet objects
    def file_to_packets(self):
        data = open(self.in_file).read()
        return self.create_packets(data, packet.MAX_DATA_LENGTH)

    # create list of packet objects from data
    def create_packets(self, data, n):
        # fist divide data into chunks of size n
        packet_datas = [data[i: i + n] for i in range(0, len(data), n)]
        # then create a packet for each datum
        return [packet(1, i % packet.SEQ_NUM_MODULO, data) for i, data in enumerate(packet_datas)]

    # listen for acks
    def listen_ack(self):
        while True:
            message = self.recv_socket.recvfrom(2048)[0]

            if message:
                message_packet = packet.parse_udp_data(message)
                self.ack_num_log.write("{}\n".format(message_packet.seq_num))

                if message_packet.type == 2: # EOT packet
                    delta = datetime.datetime.now() - self.start_time
                    total_ms = int(delta.total_seconds() * 1000)
                    self.time_log.write("{}\n".format(total_ms))
                    break

                self.lock.acquire()

                # valid ack received, so update the window positions
                if self.last_acked == len(self.packets) - 1 or \
                    message_packet.seq_num != self.last_acked % packet.SEQ_NUM_MODULO:
                    self.base += 1
                    self.acked_packets += 1
                    self.last_acked += 1
                self.lock.release()

    # send a single packet object to server
    def send_packet(self, pkt):
        self.seq_num_log.write("{}\n".format(pkt.seq_num))
        self.out_socket.sendto(pkt.get_udp_data(), (self.emu_addr, self.emu_port))

    # send all data to server
    def send(self):
        self.timer.start()

        # while we still have unreceived packets to send
        while self.acked_packets < len(self.packets):

            if self.timeout:
                # send all packets from base to next sequence num
                for i in range(self.base, self.next_seq_num):
                    self.send_packet(self.packets[i])

                self.lock.acquire()
                self.timeout = False
                self.lock.release()

                # start new timer
                self.timer = threading.Timer(TIMEOUT, self.has_timeout)
                self.timer.start()

            self.lock.acquire()
            # we are still within the window
            if self.next_seq_num < len(self.packets) and self.next_seq_num < self.base + WINDOW:
                self.send_packet(self.packets[self.next_seq_num])
                self.next_seq_num += 1
            self.lock.release()

        # all packets have been received, send eot packet
        eot_packet = packet.create_eot(len(self.packets) % packet.SEQ_NUM_MODULO)
        self.send_packet(eot_packet)

    # init and run threads for listening to acks and sending data
    def run(self):
        send_thread = threading.Thread(target=self.send)
        listen_thread = threading.Thread(target=self.listen_ack)
        listen_thread.start()
        self.start_time = datetime.datetime.now()
        send_thread.start()


if __name__ == "__main__":
    if (len(sys.argv) != 5):
        sys.exit("Invalid command line args: see documentation.txt")

    emu_addr = sys.argv[1]
    emu_port = int(sys.argv[2])
    recv_port = int(sys.argv[3])
    in_file = sys.argv[4]

    sender = Sender(emu_addr, emu_port, recv_port, in_file)

    print("running sender...")
    sender.run()
