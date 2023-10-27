from typing import Union

from ...types.update import Update


class PausedStream(Update):
    def __init__(
        self,
        chat_id: Union[int, str],
    ):
        super().__init__(chat_id)
