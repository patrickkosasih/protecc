import random


class Codec:
    def __init__(self, seed: int):
        # Fields
        self.seed = seed
        self.byte_key = []
        self.reverse_byte_key = []

        self.set_seed(seed)

    def set_seed(self, seed: int):
        self.seed = seed
        self.byte_key = [x for x in range(256)]
        random.Random(seed).shuffle(self.byte_key)

        self.reverse_byte_key = [self.byte_key.index(x) for x in range(256)]

    def encrypt(self, s: bytes) -> bytes:
        return bytes(self.byte_key[x] for x in s)

    def decrypt(self, s: bytes) -> bytes:
        return bytes(self.reverse_byte_key[x] for x in s)


