"""
shared.py
A shared module containing constants and functions that is used in multiple other modules
"""
import time

SYMBOLS = " !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
PASS_DOT = chr(0x2022)


def valid_char(p) -> bool:
    return p.isalpha() or p.isnumeric() or p in SYMBOLS


def measure(func):
    # A decorator to measure the time taken to run a function
    def wrapper(*args, **kwargs):
        time_before = time.perf_counter()
        ret = func(*args, **kwargs)  # Call function
        time_taken = time.perf_counter() - time_before

        print(f"{func.__name__} took {time_taken} seconds to run")
        return ret

    return wrapper
