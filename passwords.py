import os
import struct

import codec


APPDATA_PATH = os.path.join(os.getenv("localappdata"), "Protecc")
PASS_PATH = os.path.join(APPDATA_PATH, "pass.bin")


def pass_file_exists():
    return os.path.isfile(PASS_PATH)


def init_pass_file(new_password: str):
    if not os.path.isdir(APPDATA_PATH):
        os.mkdir(APPDATA_PATH)

    change_password(new_password)


def change_password(new_password: str):
    with open(PASS_PATH, "wb") as f:
        f.write(struct.pack("q", hash(new_password)))


def check_password(password: str) -> bool:
    with open(PASS_PATH, "rb") as f:
        correct_pass_bytes = f.read()

    correct_pass_hash: int = struct.unpack("q", correct_pass_bytes)[0]
    input_pass_hash = hash(password)

    return correct_pass_hash == input_pass_hash
