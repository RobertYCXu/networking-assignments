"""
Peer class.
"""

import json
import random
import sys
import threading
from socket import (
    socket,
    AF_INET,
    SOCK_STREAM
)
from p2pfile import P2PFile, CHUNK_SIZE
from packet import packet

MAX_SEND_CHUNKS = 2000
SOCKET_TIMEOUT = 3

class Peer():
    def __init__(self, tracker_addr, tracker_port, min_alive_time):
        # TRACKER
        self.tracker_addr = tracker_addr
        self.tracker_port = tracker_port

        self.min_alive_time = min_alive_time

        # SOCKET TO LISTEN TO TRACKER
        self.listen_sock = socket(AF_INET, SOCK_STREAM)
        self.listen_sock.bind(('', 0))
        self.listen_sock_port = self.listen_sock.getsockname()[1]
        self.listen_sock.settimeout(SOCKET_TIMEOUT)

        # UPLOAD SOCKET
        self.upload_sock = socket(AF_INET, SOCK_STREAM)
        self.upload_sock.bind(('', 0))
        self.upload_sock_port = self.upload_sock.getsockname()[1]
        self.upload_sock.settimeout(SOCKET_TIMEOUT)

        # VARIABLES
        self.id = None
        self.cur_info = {}
        self.my_orig_files = P2PFile.get_all_info_in_shared()
        self.timer_started = False
        self.all_files = {}
        self.completed_files = {file_info["filename"] for file_info in self.my_orig_files}
        self.disconnect = False

        # TIMER
        self.timer = threading.Timer(self.min_alive_time, self.timeout)

        # THREADS
        self.listen_to_tracker_thread = threading.Thread(target=self.listen_to_tracker)
        self.download_files_thread = threading.Thread(target=self.download_files, daemon=True)
        self.upload_files_thread = threading.Thread(target=self.upload_files, daemon=True)
        self.check_disconnect_thread = threading.Thread(target=self.check_disconnect, daemon=True)

        # LOCK
        self.lock = threading.Lock()

    def timeout(self):
        tracker_sock = socket(AF_INET, SOCK_STREAM)
        tracker_sock.connect((self.tracker_addr, self.tracker_port))
        msg = {
            "type": "DISCONNECT",
            "id": self.id

        }
        packet.send_msg(tracker_sock, json.dumps(msg).encode())
        all_files = P2PFile.get_all_info_in_shared()
        print("PEER {} SHUTDOWN: HAS {}".format(
            self.id,
            len(all_files)
        ))
        for fileinfo in all_files:
            print("{}    {}".format(
                self.id,
                fileinfo["filename"]
            ))
        self.disconnect = True

    def has_all_files(self):
        with self.lock:
            # check I have everyone's files
            for filename in self.cur_info["info"]:
                if filename not in self.completed_files:
                    return False

            # check if everyone has my file
            for peer_info in self.cur_info["peers"]:
                if not peer_info:
                    continue
                peer_id = peer_info["id"]
                if peer_id == self.id:
                    continue
                for fileinfo in self.my_orig_files:
                    peer_file_info = self.cur_info["info"][fileinfo["filename"]]["peers"][peer_id]
                    if not peer_file_info or peer_file_info["cur_chunk"] != fileinfo["numchunks"]:
                        return False
            return True


    def connect_to_tracker(self):
        tracker_sock = socket(AF_INET, SOCK_STREAM)
        tracker_sock.connect((self.tracker_addr, self.tracker_port))
        msg = {
            "type": "CONNECT",
            "file_info": self.my_orig_files,
            "upload_port": self.upload_sock_port,
            "listen_port": self.listen_sock_port
        }
        packet.send_msg(tracker_sock, json.dumps(msg).encode())
        self.id = int(packet.recv_msg(tracker_sock).decode())
        tracker_sock.close()

    def upload_files(self):
        self.upload_sock.listen(1)
        while True:
            try:
                peer_sock, addr = self.upload_sock.accept()
            except:
                if self.disconnect:
                    break
                continue
            peer_msg = json.loads(packet.recv_msg(peer_sock).decode())
            msg = P2PFile.get_bytes_from_file_in_shared(
                peer_msg["filename"],
                peer_msg["start_chunk"],
                peer_msg["end_chunk"]
            )
            packet.send_msg(peer_sock, msg)
            # peer_sock.send(msg)
            peer_sock.close()

    def update_tracker(self, filename, cur_chunk):
        while True:
            try:
                tracker_sock = socket(AF_INET, SOCK_STREAM)
                tracker_sock.connect((self.tracker_addr, self.tracker_port))
                msg = {
                    "id": self.id,
                    "type": "DOWNLOADED",
                    "filename": filename,
                    "cur_chunk": cur_chunk
                }
                packet.send_msg(tracker_sock, json.dumps(msg).encode())
                tracker_sock.close()
                break
            except:
                continue


    def download_files(self):
        while True:
            if self.disconnect:
                break
            if not self.cur_info:
                continue
            else:
                filenames = []
                for filename in self.cur_info["info"]:
                    if filename not in self.completed_files:
                        filenames.append(filename)

                if len(filenames) == 0:
                    continue

                chosen_file = random.choice(filenames)

                potential_peers = []

                for peer in self.cur_info["info"][chosen_file]["peers"]:
                    if peer is not None:
                        if chosen_file not in self.all_files:
                            self.all_files[chosen_file] = {
                                "cur_chunk": 0,
                            }
                        if self.all_files[chosen_file]["cur_chunk"] < peer["cur_chunk"]:
                            potential_peers.append(peer)

                chosen_peer = random.choice(potential_peers)
                start_chunk = self.all_files[chosen_file]["cur_chunk"]
                end_chunk = min(
                    start_chunk + MAX_SEND_CHUNKS,
                    self.cur_info["info"][chosen_file]["info"]["numchunks"]
                )

                download_socket = socket(AF_INET, SOCK_STREAM)

                try:
                    download_socket.connect((chosen_peer["addr"], chosen_peer["upload_port"]))
                    msg = {
                        "filename": chosen_file,
                        "start_chunk": start_chunk,
                        "end_chunk": end_chunk
                    }
                    packet.send_msg(download_socket, json.dumps(msg).encode())
                    peer_msg = packet.recv_msg(download_socket)
                except:
                    continue

                P2PFile.write_to_file(chosen_file, peer_msg)

                download_socket.close()

                self.all_files[chosen_file]["cur_chunk"] = end_chunk

                if end_chunk == self.cur_info["info"][chosen_file]["info"]["numchunks"]:
                    self.completed_files.add(chosen_file)

                # send update to tracker
                self.update_tracker(chosen_file, end_chunk)


    def listen_to_tracker(self):
        self.listen_sock.listen(1)
        while True:
            try:
                tracker_socket, addr = self.listen_sock.accept()
            except:
                if self.disconnect:
                    break
                continue
            with self.lock:
                self.cur_info = json.loads(packet.recv_msg(tracker_socket).decode())
            tracker_socket.close()

    def check_disconnect(self):
        while True:
            if self.disconnect:
                break
            if not self.cur_info:
                continue
            if self.has_all_files():
                if not self.timer_started:
                    self.timer_started = True
                    self.timer.start()
            else:
                self.timer.cancel()
                self.timer = threading.Timer(self.min_alive_time, self.timeout)
                self.timer_started = False

    def run(self):
        self.listen_to_tracker_thread.start()
        self.connect_to_tracker()
        self.download_files_thread.start()
        self.upload_files_thread.start()
        self.check_disconnect_thread.start()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("Usage: python peer.py <tracker_addr> <tracker_port> <min_alive_time>")

    tracker_addr = sys.argv[1]
    tracker_port = sys.argv[2]
    min_alive_time = sys.argv[3]

    peer = Peer(tracker_addr, int(tracker_port), int(min_alive_time))
    peer.run()
