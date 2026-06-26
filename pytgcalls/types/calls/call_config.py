from typing import Optional
from typing import Union


class CallConfig:
    def __init__(
        self,
        timeout: int = 60,
        conference: Optional[Union[bool, int]] = False,
    ):
        self.timeout: int = timeout
        self.conference: Optional[Union[bool, int]] = conference
