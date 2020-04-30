"""
Class to represent a p2pfile in our network. Also has utility functions for obtaining bytes and
writing bytes to files.
"""

import math
import os
import json

CHUNK_SIZE = 512 # bytes
SHARED_DIR = "./Shared"

class P2PFile:
    def __init__(self, filename, filesize=None):
        self.filename = filename
        self.filesize = filesize if filesize else os.path.getsize(
            os.path.join(SHARED_DIR, filename)
        )
        self.numchunks = math.ceil(self.filesize / CHUNK_SIZE)
        self.last_chunk_size = self.filesize % CHUNK_SIZE

    def get_info(self):
        return {
            "filename": self.filename,
            "filesize": self.filesize,
            "numchunks": self.numchunks,
            "last_chunk_size": self.last_chunk_size
        }

    @staticmethod
    def list_files(directory):
        return os.listdir(directory)

    @staticmethod
    def file_from_info(info):
        return P2PFile(
            info["filename"],
            info["filesize"],
        )

    @staticmethod
    def get_all_info(directory):
        return [P2PFile(filename).get_info() for filename in P2PFile.list_files(directory)]

    @staticmethod
    def get_all_info_in_shared():
        return P2PFile.get_all_info(SHARED_DIR)

    @staticmethod
    def load_file_info(file_info_dict):
        return P2PFile(file_info_dict["filename"], file_info_dict["filesize"])

    @staticmethod
    def bytes_from_file(filename, start_chunk, end_chunk, chunksize=CHUNK_SIZE):
        start_byte = start_chunk * CHUNK_SIZE
        with open(filename, "rb") as f:
            f.seek(start_byte)
            while True:
                chunk = f.read(chunksize)
                if not chunk:
                    break
                yield chunk

    @staticmethod
    def get_bytes_from_file_in_shared(filename, start_chunk, end_chunk):
        fname = os.path.join(SHARED_DIR, filename)
        file_bytes = None
        cur_chunk = start_chunk
        for b in P2PFile.bytes_from_file(fname, start_chunk, end_chunk):
            if not file_bytes:
                file_bytes = b
            else:
                file_bytes += b
            cur_chunk += 1
            if cur_chunk == end_chunk:
                break
        return file_bytes

    @staticmethod
    def write_to_file(filename, file_bytes, directory=SHARED_DIR):
        fname = os.path.join(directory, filename)
        with open(fname, "ab") as f:
            f.write(file_bytes)
