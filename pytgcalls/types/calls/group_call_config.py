from typing import Any


class GroupCallConfig:
    def __init__(
        self,
        invite_hash: str | None = None,
        join_as: Any = None,
        auto_start: bool = True,
    ):
        self.invite_hash: str | None = invite_hash
        self.join_as: Any = join_as
        self.auto_start: bool = auto_start
