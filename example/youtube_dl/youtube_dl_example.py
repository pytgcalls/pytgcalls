from pyrogram import Client

from pytgcalls import idle
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioQuality
from pytgcalls.types import MediaStream
from pytgcalls.types import VideoQuality

app = Client(
    'py-tgcalls',
    api_id=123456789,
    api_hash='abcdef12345',
)

call_py = PyTgCalls(app)
call_py.start()
call_py.join_group_call(
    -1001234567890,
    MediaStream(
        'https://www.youtube.com/watch?v=msiLgFkXvD8',
        audio_parameters=AudioQuality.HIGH,
        video_parameters=VideoQuality.HD_720p,
    ),
)
idle()
