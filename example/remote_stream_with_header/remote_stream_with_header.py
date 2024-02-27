from pyrogram import Client

from pytgcalls import idle
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioQuality
from pytgcalls.types import Browsers
from pytgcalls.types import MediaStream
from pytgcalls.types import VideoQuality

app = Client(
    'py-tgcalls',
    api_id=123456789,
    api_hash='abcdef12345',
)

call_py = PyTgCalls(app)
call_py.start()
remote = 'http://docs.evostream.com/sample_content/assets/sintel1m720p.mp4'
call_py.play(
    -1001234567890,
    MediaStream(
        remote,
        AudioQuality.HIGH,
        VideoQuality.HD_720p,
        headers={
            'User-Agent': Browsers().chrome_windows,
        },
    ),
)
idle()
