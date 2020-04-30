"""Interface for running client."""

import sys
from message_board import MessageBoardClient


if __name__ == "__main__":
    if (len(sys.argv) != 5):
        sys.exit("Usage: python client.py <server_address> <n_port> <req_code> <msg>")

    server_name = sys.argv[1]
    server_port = int(sys.argv[2])
    req_code = sys.argv[3]
    message = sys.argv[4]

    # create client object and send message to server
    mbc = MessageBoardClient(req_code, server_name, server_port)

    # if invalid req code, send_message returns exit code 1 and the program should stop
    if mbc.send_message(message):
        sys.exit()

    input("Press any key to exit.")
