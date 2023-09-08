from typing import Union

from ...types.update import Update


class ChangedStream(Update):
    def __init__(
        self,
        chat_id: Union[int, str],
    ):
        super().__init__(chat_id)
