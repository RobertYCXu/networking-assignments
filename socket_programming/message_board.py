"""Library classes for the message board client, server, and socket."""

import os
from socket import (
    socket,
    AF_INET,
    SOCK_STREAM,
    SOCK_DGRAM
)
import threading

class MessageBoardSocket():
    # dynamically create either UDP or TCP socket based on sock_type
    def __init__(self, sock_type):
        self.sock = socket(AF_INET, sock_type)

        # bind socket to any open port
        self.sock.bind(('', 0))
        self.port = self.sock.getsockname()[1]


class MessageBoardServer():
    def __init__(self, req_code):
        self.tcp_socket = MessageBoardSocket(SOCK_STREAM)
        self.req_code = req_code
        self.messages = []
        self.messages_lock = threading.Lock()

    def send_messages_to_client(self, client_address, udp_socket):
        # lock messages array
        self.messages_lock.acquire()
        for message in self.messages:
            udp_socket.sock.sendto(message.encode(), client_address)
        udp_socket.sock.sendto("NO MSG.".encode(), client_address)
        # release lock
        self.messages_lock.release()


    def recieve_messages(self, udp_socket, client_port):
        # recieve client's messages
        while True:
            message, client_address = udp_socket.sock.recvfrom(2048)

            if message:
                message = message.decode()

                # if message is "GET" send all server messages to client
                if message == "GET":
                    self.send_messages_to_client(client_address, udp_socket)

                # terminate program
                elif message == "TERMINATE":
                    os._exit(1)

                # format message, then append to list of client messages
                else:
                    # lock messages array
                    self.messages_lock.acquire()
                    self.messages.append(self.format_message(client_port, message))
                    # release lock
                    self.messages_lock.release()

    def format_message(self, client_port, message):
        return "[{}]: {}".format(client_port, message)

    def listen_to_clients(self):
        authentication_socket, addr = self.tcp_socket.sock.accept()
        client_req_code = authentication_socket.recv(1024).decode()
        client_port = addr[1]

        if client_req_code:
            # send to the client either "0" if req code is incorrect or the newly created server
            # udp port if the code is correct
            if client_req_code != self.req_code:
                authentication_socket.send("0".encode())
            else:
                udp_socket = MessageBoardSocket(SOCK_DGRAM)
                authentication_socket.send(str(udp_socket.port).encode())

                udp_thread = threading.Thread(
                    target=self.recieve_messages,
                    args=(udp_socket, client_port),
                    daemon=True
                )
                udp_thread.start()

        # close TCP socket used to authenticate client
        authentication_socket.close()

    def run(self):
        print("SERVER_PORT={}".format(
            self.tcp_socket.port
        ))
        self.tcp_socket.sock.listen(1)
        while True:
            self.listen_to_clients()


class MessageBoardClient():
    def __init__(self, req_code, server_name, server_port_tcp):
        self.tcp_socket = MessageBoardSocket(SOCK_STREAM)
        self.udp_socket = MessageBoardSocket(SOCK_DGRAM)
        self.req_code = req_code
        self.server_name = server_name
        self.tcp_socket.sock.connect((server_name, server_port_tcp))

    def get_server_port(self):
        # send req_code to get server UDP port
        self.tcp_socket.sock.send(self.req_code.encode())
        return self.tcp_socket.sock.recv(1024).decode()

    def get_server_messages(self, udp_port):
        # first send "GET" message to have server send back its stored messages
        self.udp_socket.sock.sendto("GET".encode(), (self.server_name, udp_port))
        while True:
            # recieve server stored messages one at a time
            message, server_address = self.udp_socket.sock.recvfrom(2048)

            if message:
                print(message.decode())

                # indicates no more messages
                if message.decode() == "NO MSG.":
                    return

    def send_message(self, message):
        udp_port = int(self.get_server_port())

        # return with exit status 1 if req code is invalid
        if udp_port == 0:
            print("Invalid req code.")
            return 1
        else:
            # get and print messages stored on server
            self.get_server_messages(int(udp_port))

            # send client message to server
            self.udp_socket.sock.sendto(message.encode(), (self.server_name, udp_port))
