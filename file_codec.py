"""
file_codec.py
"""

import os
import random
import struct
from typing import Callable

import codec


SEED_RANGE = -(2 ** 63), 2 ** 63  # 64 bit range


def hide_file(file, unhide=False):
    plus_minus = "-" if unhide else "+"
    os.system(f"attrib {plus_minus}h {file}")


def encrypt_file(file_path: str) -> bool:
    file_ext = os.path.splitext(file_path)[1]
    if file_ext == ".protecclock":
        return False

    # print(f"Encrypting {file_path}")

    with open(file_path, "rb") as f:
        raw = f.read()

    key = random.randrange(*SEED_RANGE)
    # print(key)
    converted = codec.Codec(key).encrypt(raw) + struct.pack("q", key)

    with open(file_path, "wb") as f:
        f.write(converted)

    os.rename(file_path, file_path + ".protecc")

    return True


# @misc.timer
def decrypt_file(file_path: str) -> bool:
    # IMPORTANT!!!!!!!! If these 3 lines of code below don't exist then files can potentially be LOST FOREVER.
    file_ext = os.path.splitext(file_path)[1]
    if file_ext != ".protecc":
        return False

    # print(f"Decrypting {file_path}")

    with open(file_path, "rb") as f:
        raw = f.read()

    # The last 8 bytes of an encrypted file is the key for decryption
    key = struct.unpack("q", raw[-8:])[0]
    converted = codec.Codec(key).decrypt(raw[:-8])

    with open(file_path, "wb") as f:
        f.write(converted)

    os.rename(file_path, os.path.splitext(file_path)[0])

    return True


class ProteccFolder:
    def __init__(self, path,
                 progress_updater: Callable[[int, int], None] = lambda current, total: None):

        self.path = path
        self.progress_updater = progress_updater

    def list_files(self):
        """
        Iterates through a list of paths of all the files in the folder codec's path.
        """
        for root, dirs, files in os.walk(self.path):
            for file in files:

                    yield os.path.join(root, file)

    @property
    def locked(self):
        return any(os.path.splitext(x)[1] == ".protecc" for x in self.list_files())

    def encrypt(self) -> int:
        files_to_encrypt = [x for x in self.list_files() if os.path.splitext(x)[1] != ".protecclock"]
        n_files = len(files_to_encrypt)

        for i, file in enumerate(files_to_encrypt):
            self.progress_updater(i, n_files)
            encrypt_file(file)

        self.progress_updater(n_files, n_files)
        return n_files

    def decrypt(self) -> int:
        files_to_decrypt = [x for x in self.list_files() if os.path.splitext(x)[1] == ".protecc"]
        n_files = len(files_to_decrypt)

        for i, file in enumerate(files_to_decrypt):
            self.progress_updater(i, n_files)
            decrypt_file(file)

        self.progress_updater(n_files, n_files)
        return n_files
