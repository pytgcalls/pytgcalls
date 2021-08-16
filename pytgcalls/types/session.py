import random
import string


class Session:
    @staticmethod
    def generate_session_id(length) -> str:
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for _ in range(length))
