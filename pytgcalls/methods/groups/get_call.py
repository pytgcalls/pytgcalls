from ...scaffold import Scaffold


class GetCall(Scaffold):
    def get_call(
        self,
        chat_id: int,
    ):
        """Check/Get an existent group call

        This method check if exist an Group Call,
        if not, this can raise an error

        Parameters:
            chat_id (``int``):
                Unique identifier (int) of the target chat.

        Raises:
            GroupCallNotFound: In case you try
                to get a non-existent group call

        Returns:
            :obj:`~pytgcalls.types.GroupCall()`: On success,
            the group call is returned.

        Example:
            .. code-block:: python
                :emphasize-lines: 10-12

                from pytgcalls import Client
                from pytgcalls import idle
                ...

                app = PyTgCalls(client1)
                app.start()

                ...  # Call API methods

                app.get_call(
                    -1001185324811,
                )

                idle()
        """
        return self._call_holder.get_call(
            chat_id,
        )
