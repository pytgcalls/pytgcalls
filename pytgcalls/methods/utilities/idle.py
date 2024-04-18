import asyncio
import logging
import signal
from signal import SIGABRT
from signal import SIGINT
from signal import signal as signal_fn
from signal import SIGTERM


py_logger = logging.getLogger('pytgcalls')

# Signal number to name
signals = {
    k: v for v, k in signal.__dict__.items()
    if v.startswith('SIG') and not v.startswith('SIG_')
}


async def idle():
    task = None

    def signal_handler(signum, __):
        py_logger.info(f'Stop signal received ({signals[signum]}). Exiting...')
        asyncio.get_event_loop().run_in_executor(None, task.cancel)

    for s in (SIGINT, SIGTERM, SIGABRT):
        signal_fn(s, signal_handler)

    while True:
        task = asyncio.create_task(asyncio.sleep(600))

        try:
            await task
        except asyncio.CancelledError:
            break
