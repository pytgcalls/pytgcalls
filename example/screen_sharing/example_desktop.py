from pyrogram import Client

from pytgcalls import idle
from pytgcalls import PyTgCalls
from pytgcalls.media_devices import MediaDevices
from pytgcalls.types import MediaStream

app = Client(
    'py-tgcalls',
    api_id=123456789,
    api_hash='abcdef12345',
)

call_py = PyTgCalls(app)
call_py.start()
call_py.play(
    -1001234567890,
    MediaStream(
        MediaDevices.get_screen_devices()[0],
    ),
)
idle()
