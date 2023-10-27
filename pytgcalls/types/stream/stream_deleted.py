from deprecation import deprecated

from ...types.update import Update


@deprecated(
    deprecated_in='1.0.0.dev1',
    removed_in='1.0.0.dev1',
    details='This method is no longer supported.',
)
class StreamDeleted(Update):
    def __init__(
            self,
            chat_id: int,
    ):
        super().__init__(chat_id)
