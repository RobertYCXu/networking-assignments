"""Interface for running server."""

import sys
from message_board import MessageBoardServer


if __name__ == "__main__":
    if (len(sys.argv) != 2):
        sys.exit("Usage: python server.py <req_code>")

    req_code = sys.argv[1]

    # create server object
    mbs = MessageBoardServer(req_code)

    # run the server
    mbs.run()
