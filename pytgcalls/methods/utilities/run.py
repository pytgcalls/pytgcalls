from ...scaffold import Scaffold
from .idle import idle


class Run(Scaffold):
    async def run(self):
        """Start the client, idle the main script and finally stop the client.

        This is a convenience method that calls start(), idle() and stop
        in sequence. It makes running a client less verbose, but is not
        suitable in case you want to run more than one client in a single
        main script, since idle() will block after starting the own client.

        Raises:
            PyTgCallsAlreadyRunning: In case you try
                to start an already started client.

        Example:
            .. code-block:: python
                :emphasize-lines: 8

                from pytgcalls import Client
                from pytgcalls import idle
                ...
                app = Client(client)

                ...  # Call API decorators / MtProto decorators

                app.run()
        """
        await self.start()
        await idle()
