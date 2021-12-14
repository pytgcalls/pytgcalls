from ...scaffold import Scaffold


class GetActiveCall(Scaffold):
    def get_active_call(
        self,
        chat_id: int,
    ):
        """Check/Get an active call

        This method check if is active an Group Call (Playing / Paused),
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

                app.get_active_call(
                    -1001185324811,
                )

                idle()
        """
        return self._call_holder.get_active_call(
            chat_id,
        )
