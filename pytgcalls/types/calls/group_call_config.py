from typing import Any
from typing import Optional


class GroupCallConfig:
    def __init__(
        self,
        invite_hash: Optional[str] = None,
        join_as: Any = None,
        auto_start: bool = True,
    ):
        self.invite_hash: Optional[str] = invite_hash
        self.join_as: Any = join_as
        self.auto_start: bool = auto_start
