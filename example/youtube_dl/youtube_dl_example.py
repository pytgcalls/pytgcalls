from pyrogram import Client

from pytgcalls import PyTgCalls
from pytgcalls import idle
from pytgcalls.types import AudioQuality
from pytgcalls.types import MediaStream
from pytgcalls.types import VideoQuality

app = Client(
    'py-tgcalls',
    api_id=123456789,
    api_hash='abcdef12345',
)

PROXY = 'http://username:password@host:port'

call_py = PyTgCalls(app)
call_py.start()
call_py.play(
    -1001234567890,
    MediaStream(
        'https://www.youtube.com/watch?v=msiLgFkXvD8',
        AudioQuality.HIGH,
        VideoQuality.HD_720p,
        ytdlp_parameters=f'--proxy {PROXY}',
        ffmpeg_parameters=f'-http_proxy {PROXY}',
    ),
)
idle()
