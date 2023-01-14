"""
filemgr.py (File manager)
"""

import os
import random
import struct

import codec
import misc

SEED_RANGE = -(2 ** 63), 2 ** 63  # 64 bit range


def list_files(dir_path: str):
    """
    Iterates through a list of paths of all the files in a directory including its subdirectories
    """
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            yield f"{root}/{file}"


# @misc.timer
def encrypt_file(file_path: str):
    with open(file_path, "rb") as f:
        raw = f.read()

    key = random.randrange(*SEED_RANGE)
    # print(key)
    converted = codec.Codec(key).encrypt(raw) + struct.pack("q", key)

    with open(file_path, "wb") as f:
        f.write(converted)

    os.rename(file_path, file_path + ".protecc")


# @misc.timer
def decrypt_file(file_path: str):
    if os.path.splitext(file_path)[1] != ".protecc":
        return

    with open(file_path, "rb") as f:
        raw = f.read()

    # The last 8 bytes of an encrypted file is the key for decryption
    key = struct.unpack("q", raw[-8:])[0]
    converted = codec.Codec(key).decrypt(raw[:-8])

    with open(file_path, "wb") as f:
        f.write(converted)

    os.rename(file_path, os.path.splitext(file_path)[0])


def encrypt_dir(dir_path: str):
    count = 0
    for file in list_files(dir_path):
        encrypt_file(file)
        count += 1
    return count


def decrypt_dir(dir_path: str):
    count = 0
    for file in list_files(dir_path):
        decrypt_file(file)
        count += 1
    return count
