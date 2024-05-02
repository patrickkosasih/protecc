import hashlib

from shared import *


SYMBOLS = " !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"

APPDATA_PATH = os.path.join(os.getenv("localappdata"), "Protecc")
PASS_PATH = os.path.join(APPDATA_PATH, "pass.bin")


def is_valid_char(c) -> bool:
    # Check if a character is a legal character for a password or not
    return c.isalpha() or c.isnumeric() or c in SYMBOLS


def is_valid_password(s: str) -> bool:
    return all(is_valid_char(x) for x in s)


def pass_file_exists():
    return os.path.isfile(PASS_PATH)


def init_pass_file(new_password: str):
    if not os.path.isdir(APPDATA_PATH):
        os.mkdir(APPDATA_PATH)

    set_password(new_password)


def set_password(new_password: str):
    m = hashlib.sha256()
    m.update(new_password.encode("utf-8"))

    with open(PASS_PATH, "wb") as f:
        f.write(m.digest())


def verify_password(password: str) -> bool:
    with open(PASS_PATH, "rb") as f:
        correct_pass_hash = f.read()

    m = hashlib.sha256()
    m.update(password.encode("utf-8"))

    input_pass_hash = m.digest()

    return correct_pass_hash == input_pass_hash
