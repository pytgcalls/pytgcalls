from pyrogram import Client

from pytgcalls import idle
from pytgcalls import PyTgCalls

app = Client(
    'py-tgcalls',
    api_id=123456789,
    api_hash='abcdef12345',
)

call_py = PyTgCalls(app)
call_py.start()
call_py.play(
    -1001234567890,
    'test.mkv',
)
idle()
