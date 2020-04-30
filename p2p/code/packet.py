"""
Helper functions for dealing with TCP packet streams. Defines custom TCP protocol where first four
bytes of a message is its size.
"""
import struct

class packet:
    @staticmethod
    def send_msg(sock, msg):
        # prefix each message with a 4-byte length (network byte order)
        msg = struct.pack('>I', len(msg)) + msg
        sock.sendall(msg)

    @staticmethod
    def recv_msg(sock):
        # read message length and unpack it into an integer
        raw_msglen = packet.recvall(sock, 4)
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        # read the message data
        return packet.recvall(sock, msglen)

    @staticmethod
    def recvall(sock, n):
        # helper function to recv n bytes or return None if EOF is hit
        data = bytearray()
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data
