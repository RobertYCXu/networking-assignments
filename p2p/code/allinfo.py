"""
Class representing information sent from tracker to peer about the entire network. Also handles
updating this information and necessary printing on updates.

STRUCTURE:

self.info:

{
    filename1: {
        info: {
            filename: "filename1",
            filesize: 1000,
            numchunks: 8,
            last_chunk_size: 400,
        }
        peers: [
            {
                upload_addr: "localhost",
                upload_port: 300,
                cur_chunk: 30
            },
            None,
            None,
            {
                ...
            }
        ]

    },
    filename2: {
        ...
    }
}

self.peers:

    [
        {id: ..., addr: ..., upload_port:..., listen_port:..., filename:..., cur_cunk:...},
        ...
    ]

"""

from peerfileinfo import PeerFileInfo
from p2pfile import P2PFile

class AllInfo:
    def __init__(self, max_peers):
        self.info = {}
        self.peers = [None] * max_peers
        self.max_peers = max_peers

    def add_peer_info(self, peer_file_info):
        peers = [None] * self.max_peers
        peers[peer_file_info.id] = peer_file_info.get_info()
        self.info[peer_file_info.filename] = {
            "info": peer_file_info.p2pfile.get_info(),
            "peers": peers
        }
        if not self.peers[peer_file_info.id]:
            self.peers[peer_file_info.id] = peer_file_info.get_info()

    def remove_peer_info(self, peer_id):
        print("PEER {} DISCONNECT: RECEIVED {}".format(
            peer_id,
            len(self.info)
        ))
        self.peers[peer_id] = None
        for fileinfo in self.info.items():
            print("{}    {}".format(
                peer_id,
                fileinfo[0]
            ))

    def update_peer_info(self, peer_id, filename, cur_chunk):
        fileinfo = self.info[filename]

        if fileinfo["peers"][peer_id] is None:
            p2pfileinfo = P2PFile.file_from_info(fileinfo["info"])
            peer_info = PeerFileInfo(
                peer_id,
                self.peers[peer_id]["addr"],
                self.peers[peer_id]["upload_port"],
                self.peers[peer_id]["listen_port"],
                p2pfileinfo
            )
            fileinfo["peers"][peer_id] = peer_info.get_info()

        print("PEER {} ACQUIRED: CHUNK {}/{} {}".format(
            peer_id,
            cur_chunk,
            fileinfo["info"]["numchunks"],
            filename
        ))
        fileinfo["peers"][peer_id]["cur_chunk"] = cur_chunk
