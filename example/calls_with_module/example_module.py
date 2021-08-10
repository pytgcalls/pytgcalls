import os
import time

from pyrogram import Client

from pytgcalls import PyLogs
from pytgcalls import PyTgCalls
from pytgcalls import StreamType

app = Client(
    'py-tgcalls',
    api_id=123456789,
    api_hash='abcdef12345',
)

call_py = PyTgCalls(
    app,
    log_mode=PyLogs.ultra_verbose,
)
if __name__ == '__main__':
    file = '../input.raw'
    while not os.path.exists(file):
        time.sleep(0.125)
    call_py.join_group_call(
        -1001234567890,
        file,
        stream_type=StreamType().local_stream,
    )
    call_py.run()
