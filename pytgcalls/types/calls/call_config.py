class CallConfig:
    def __init__(
        self,
        timeout: int = 60,
        conference: bool = False,
    ):
        self.timeout: int = timeout
        self.conference: bool = conference
