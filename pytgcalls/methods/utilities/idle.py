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
