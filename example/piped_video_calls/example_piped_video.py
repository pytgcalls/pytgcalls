from pyrogram import Client

from pytgcalls import idle
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioVideoPiped

app = Client(
    'py-tgcalls',
    api_id=123456789,
    api_hash='abcdef12345',
)

call_py = PyTgCalls(app)
call_py.start()
video_file = 'test.mkv'
call_py.join_group_call(
    -1001234567890,
    AudioVideoPiped(
        video_file,
    ),
)
idle()
