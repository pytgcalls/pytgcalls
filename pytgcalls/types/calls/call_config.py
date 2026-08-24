class CallConfig:
    def __init__(
        self,
        timeout: int = 60,
        conference: bool | int | None = False,
    ):
        self.timeout: int = timeout
        self.conference: bool | int | None = conference
