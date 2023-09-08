import deprecation

from ...types.update import Update


@deprecation.deprecated(
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
