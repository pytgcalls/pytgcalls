from ntgcalls import Format
from ntgcalls import MediaSource
from pyrogram import Client

from pytgcalls import PyTgCalls
from pytgcalls import idle
from pytgcalls.types.raw import AudioParameters
from pytgcalls.types.raw import AudioStream
from pytgcalls.types.raw import Stream

app = Client(
    'py-tgcalls',
    api_id=123456789,
    api_hash='abcdef12345',
)

call_py = PyTgCalls(app)
call_py.start()
call_py.play(
    -1001234567890,
    Stream(
        AudioStream(
            MediaSource.FILE,
            'input.opus',
            AudioParameters(
                sample_rate=48000,
                channels=2,
                bitrate=192000,
            ),
            format=Format.OGG,
        ),
    ),
)
idle()
