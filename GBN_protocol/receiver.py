import sys
from socket import (
    socket,
    AF_INET,
    SOCK_DGRAM
)

from packet import packet

if __name__ == "__main__":
    if (len(sys.argv) != 5):
        sys.exit("Invalid command line args: see documentation.txt")

    print("running reveiver...")

    emu_addr = sys.argv[1]
    emu_port = int(sys.argv[2])
    recv_port = int(sys.argv[3])
    out_file = sys.argv[4]

    out_socket = socket(AF_INET, SOCK_DGRAM)

    recv_socket = socket(AF_INET, SOCK_DGRAM)
    recv_socket.bind(('', recv_port))

    expected_seq_num = 0
    cur_packet_seq_num = 0
    done_first_packet = False # for detecting first packet with seq num 0

    out_file_stream = open(out_file, "w")
    arrival_log = open("arrival.log", "w")

    # listen to messages
    while True:
        message = recv_socket.recvfrom(2048)[0]

        if message:
            message_packet = packet.parse_udp_data(message)
            arrival_log.write("{}\n".format(message_packet.seq_num))
            ack_packet = None

            if message_packet.seq_num == expected_seq_num:
                done_first_packet = True
                cur_packet_seq_num = expected_seq_num

                if message_packet.type == 1:
                    out_file_stream.write(message_packet.data)

                expected_seq_num = (expected_seq_num + 1) % packet.SEQ_NUM_MODULO

            elif not done_first_packet:
                continue

            else:
                cur_packet_seq_num = \
                    (packet.SEQ_NUM_MODULO + (expected_seq_num - 1)) % packet.SEQ_NUM_MODULO

            # send ack
            if message_packet.type == 2: # EOT
                ack_packet = packet.create_eot(cur_packet_seq_num)
            else:
                ack_packet = packet.create_ack(cur_packet_seq_num)

            out_socket.sendto(packet.get_udp_data(ack_packet), (emu_addr, emu_port))

            if message_packet.type == 2: # since we got EOT, exit
                break

    out_file_stream.close()
