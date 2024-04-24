"""
filemgr.py (File manager)
"""

import os
import random
import struct

import codec

SEED_RANGE = -(2 ** 63), 2 ** 63  # 64 bit range


def list_files(dir_path: str):
    """
    Iterates through a list of paths of all the files in a directory including its subdirectories
    """
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            yield f"{root}/{file}"


# @misc.timer
def encrypt_file(file_path: str) -> bool:
    file_ext = os.path.splitext(file_path)[1]
    if file_ext == ".protecclock":
        return False

    print(f"Encrypting {file_path}")

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

    print(f"Decrypting {file_path}")

    with open(file_path, "rb") as f:
        raw = f.read()

    # The last 8 bytes of an encrypted file is the key for decryption
    key = struct.unpack("q", raw[-8:])[0]
    converted = codec.Codec(key).decrypt(raw[:-8])

    with open(file_path, "wb") as f:
        f.write(converted)

    os.rename(file_path, os.path.splitext(file_path)[0])

    return True


def encrypt_folder(dir_path: str):
    count = 0
    for file in list_files(dir_path):
        a = encrypt_file(file)
        if a:
            count += 1
    return count


def decrypt_folder(dir_path: str):
    count = 0
    for file in list_files(dir_path):
        a = decrypt_file(file)
        if a:
            count += 1
    return count
