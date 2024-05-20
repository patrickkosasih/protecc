"""
file_manager.py
"""

import os
import random
import struct
import multiprocessing as mp
from typing import Callable

import cipher
from shared import func_timer

SEED_RANGE = -(2 ** 63), 2 ** 63  # 64 bit range
# progress_updater = lambda current, total: None


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
    converted = cipher.Codec(key).encrypt(raw) + struct.pack("q", key)

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
    converted = cipher.Codec(key).decrypt(raw[:-8])

    with open(file_path, "wb") as f:
        f.write(converted)

    os.rename(file_path, os.path.splitext(file_path)[0])

    return True


class ProteccFolder:
    def __init__(self, path,
                 progress_updater: Callable[[int, int], None] = lambda current, total: None):

        self.path = path
        self.progress_updater = progress_updater

        self.busy = False

    def list_files(self):
        """
        Iterates through a list of paths of all the files in the folder's path.
        """
        for root, dirs, files in os.walk(self.path):
            for file in files:
                yield os.path.join(root, file)

    @property
    def locked(self):
        return any(os.path.splitext(x)[1] == ".protecc" for x in self.list_files())

    # @func_timer
    def encrypt(self):
        files = [x for x in self.list_files() if os.path.splitext(x)[1] != ".protecclock"]
        self._encrypt_decrypt(True, files)

    # @func_timer
    def decrypt(self):
        files = [x for x in self.list_files() if os.path.splitext(x)[1] == ".protecc"]
        self._encrypt_decrypt(False, files)

    def _encrypt_decrypt(self, encrypt: bool, files: list[str]):
        """
        The sub-method that is called by both the encrypt and decrypt methods.

        :param encrypt: True - encrypt, False - decrypt
        :param files: List of file paths to encrypt.
        """

        assert not self.busy, "this folder is currently busy encrypting/decrypting files"

        self.busy = True

        files = sorted(files, key=os.path.getsize, reverse=True)
        n_files = len(files)
        self.progress_updater(0, n_files)

        q = mp.Queue()
        for x in files:
            q.put(x)

        processes = []
        for i in range(mp.cpu_count()):
            p = mp.Process(target=self._encrypt_decrypt_process, args=(q, encrypt))
            processes.append(p)
            p.start()

        while (files_left := q.qsize()) > 0:
            self.progress_updater(n_files - files_left, n_files)

        for p in processes:
            p.join()

        self.progress_updater(n_files + 1, n_files)
        self.busy = False

    @staticmethod
    def _encrypt_decrypt_process(file_queue: mp.Queue, encrypt: bool) -> None:
        """
        The function that is run by each process/CPU core during multiprocessing.

        :param file_queue: Multiprocessing queue of the files
        :param encrypt: True - encrypt, False - decrypt.
        """
        cipher_func = encrypt_file if encrypt else decrypt_file

        while not file_queue.empty():
            try:
                cipher_func(file_queue.get())
            except PermissionError:
                pass
