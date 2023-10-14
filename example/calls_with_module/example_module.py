import os
import time

from ntgcalls import InputMode
from pyrogram import Client

from pytgcalls import idle
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioStream
from pytgcalls.types.input_stream import Stream

app = Client(
    'py-tgcalls',
    api_id=123456789,
    api_hash='abcdef12345',
)

call_py = PyTgCalls(app)
call_py.start()
file = '../input.raw'
while not os.path.exists(file):
    time.sleep(0.125)
call_py.join_group_call(
    -1001234567890,
    Stream(
        AudioStream(
            input_mode=InputMode.File,
            path=file,
        ),
    ),
)
idle()
