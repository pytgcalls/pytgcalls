from typing import Optional


class CallConfig:
    def __init__(
        self,
        timeout: int = 60,
    ):
        self.timeout: int = timeout
