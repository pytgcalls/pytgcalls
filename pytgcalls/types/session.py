import string
from math import ceil
from math import log
from os import urandom


class Session:
    @staticmethod
    def generate_session_id(length: int = 21) -> str:
        alphabet = f'_-{string.digits}{string.ascii_letters}'
        alphabet_len = len(alphabet)

        mask = 1
        if alphabet_len > 1:
            mask = (2 << int(log(alphabet_len - 1) / log(2))) - 1
        step = int(ceil(1.6 * mask * length / alphabet_len))

        session_id = ''
        while True:
            random_bytes = bytearray(urandom(step))

            for i in range(step):
                random_byte = random_bytes[i] & mask
                if random_byte < alphabet_len:
                    if alphabet[random_byte]:
                        session_id += alphabet[random_byte]

                        if len(session_id) == length:
                            return session_id
