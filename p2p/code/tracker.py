"""
Tracker class.
"""

import json
from socket import (
    socket,
    AF_INET,
    SOCK_STREAM
)
import threading
from p2pfile import P2PFile
from peerfileinfo import PeerFileInfo
from allinfo import AllInfo
from packet import packet

PORT_FILE = "port.txt"
MAX_PEERS = 8
UPDATE_INTERVAL = 5

class Tracker():
    def __init__(self):
        self.cur_peer_num = 0
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.bind(('', 0))
        self.port = self.sock.getsockname()[1]
        self.write_port_to_file(PORT_FILE, self.port)
        self.all_info = AllInfo(MAX_PEERS)

    def write_port_to_file(self, filename, port):
        port_file = open("port.txt", "w")
        port_file.write("{}\n".format(port))
        port_file.close()

    def update_peers(self):
        for i in range(0, MAX_PEERS):
            if self.all_info.peers[i]:
                update_peer_sock = socket(AF_INET, SOCK_STREAM)
                peer_info = self.all_info.peers[i]
                update_peer_sock.connect((peer_info["addr"], peer_info["listen_port"]))
                msg = {
                    "info": self.all_info.info,
                    "peers": self.all_info.peers
                }
                packet.send_msg(update_peer_sock, json.dumps(msg).encode())
                update_peer_sock.close()

    def update_peers_periodic(self):
        self.update_peers()
        threading.Timer(UPDATE_INTERVAL, self.update_peers_periodic).start()

    def output_peer_files(self, peer_num, files_info):
        print("PEER {} CONNECT: OFFERS {}".format(
            peer_num,
            len(files_info)
        ))

        for file_info in files_info:
            print("{}    {} {}".format(
                peer_num,
                file_info.filename,
                file_info.numchunks
            ))

    def listen_to_peers(self):
        self.sock.listen(1)
        while True:
            peer_socket, addr = self.sock.accept()
            peer_addr = addr[0]
            peer_port = addr[1]

            peer_msg = json.loads(packet.recv_msg(peer_socket).decode())

            if peer_msg["type"] == "CONNECT":
                packet.send_msg(peer_socket, str(self.cur_peer_num).encode())
                files_info = []

                for file_info in peer_msg["file_info"]:
                    p2pfile = P2PFile.load_file_info(file_info)
                    files_info.append(p2pfile)
                    peer_file_info = PeerFileInfo(
                        self.cur_peer_num,
                        peer_addr,
                        peer_msg["upload_port"],
                        peer_msg["listen_port"],
                        p2pfile,
                        complete=True
                    )
                    self.all_info.add_peer_info(peer_file_info)

                self.output_peer_files(self.cur_peer_num, files_info)
                self.cur_peer_num += 1

            elif peer_msg["type"] == "DISCONNECT":
                self.all_info.remove_peer_info(int(peer_msg["id"]))

            elif peer_msg["type"] == "DOWNLOADED":
                peer_id = peer_msg["id"]
                filename = peer_msg["filename"]
                cur_chunk = peer_msg["cur_chunk"]
                self.all_info.update_peer_info(peer_id, filename, cur_chunk)

            self.update_peers()
            peer_socket.close()

    def run(self):
        self.update_peers_periodic()
        self.listen_to_peers()

if __name__ == "__main__":
    tracker = Tracker()
    tracker.run()
