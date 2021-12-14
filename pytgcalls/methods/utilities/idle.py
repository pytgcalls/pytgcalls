import asyncio
import logging
import signal
from signal import SIGABRT
from signal import SIGINT
from signal import signal as signal_fn
from signal import SIGTERM


py_logger = logging.getLogger('pytgcalls')

is_idling = False

# Signal number to name
signals = {
    k: v for v, k in signal.__dict__.items()
    if v.startswith('SIG') and not v.startswith('SIG_')
}


async def idle():
    """Block the main script execution until a signal is received.

    This function will run indefinitely in order to block the main
    script execution and prevent it from exiting while having client(s)
    that are still running in the background.

    The way PyTgCalls works, it will keep your handlers in a pool of
    worker threads, which are executed concurrently outside the main
    thread; calling idle() will ensure the client(s) will be kept alive
    by not letting the main script to end, until you decide to quit.

    Once a signal is received (e.g.: from CTRL+C) the function will
    terminate and your main script will continue.

    Example:
        .. code-block:: python
            :emphasize-lines: 15

            from pytgcalls import Client
            from pytgcalls import idle
            ...

            app1 = PyTgCalls(client1)
            app2 = PyTgCalls(client2)
            app3 = PyTgCalls(client3)

            ...  # Set handlers up

            app1.start()
            app2.start()
            app3.start()

            idle()
    """
    global is_idling

    def signal_handler(signum, __):
        global is_idling
        py_logger.info(f'Stop signal received ({signals[signum]}). Exiting...')
        is_idling = False
    for s in (SIGINT, SIGTERM, SIGABRT):
        signal_fn(s, signal_handler)
    is_idling = True
    while is_idling:
        await asyncio.sleep(1)
