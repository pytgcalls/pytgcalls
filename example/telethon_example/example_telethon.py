import os
import time

from telethon import TelegramClient

from pytgcalls import idle
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioStream
from pytgcalls.types import Stream

app = TelegramClient(
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
            file,
        ),
    ),
)
idle()
