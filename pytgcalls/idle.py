import asyncio
import logging
from signal import SIGABRT
from signal import SIGINT
from signal import signal
from signal import SIGTERM

log = logging.getLogger(__name__)

is_idling = False


async def idle():
    global is_idling

    def signal_handler(_, __):
        global is_idling
        logging.info(f'Stop signal received ({_}). Exiting...')
        is_idling = False
    for s in (SIGINT, SIGTERM, SIGABRT):
        signal(s, signal_handler)
    is_idling = True
    while is_idling:
        await asyncio.sleep(1)
