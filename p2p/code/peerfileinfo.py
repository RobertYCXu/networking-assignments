"""This class combines peer information with a file it currently has"""

from p2pfile import P2PFile

class PeerFileInfo:
    def __init__(
        self,
        idnum,
        addr,
        upload_port,
        listen_port,
        p2pfile,
        complete=False,
        cur_chunk=0
    ):
        self.id = idnum
        self.addr = addr
        self.upload_port = upload_port
        self.listen_port = listen_port
        self.p2pfile = p2pfile
        self.cur_chunk = p2pfile.numchunks if complete else cur_chunk
        self.filename = self.p2pfile.filename

    def get_info(self):
        return {
            "id": self.id,
            "addr": self.addr,
            "upload_port": self.upload_port,
            "listen_port": self.listen_port,
            "filename": self.filename,
            "cur_chunk": self.cur_chunk
        }
