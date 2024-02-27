import os
import time

from ntgcalls import InputMode
from pyrogram import Client

from pytgcalls import idle
from pytgcalls import PyTgCalls
from pytgcalls.types.raw import AudioParameters
from pytgcalls.types.raw import AudioStream
from pytgcalls.types.raw import Stream
from pytgcalls.types.raw import VideoParameters
from pytgcalls.types.raw import VideoStream

app = Client(
    'py-tgcalls',
    api_id=123456789,
    api_hash='abcdef12345',
)

call_py = PyTgCalls(app)
call_py.start()
audio_file = 'audio.raw'
video_file = 'video.raw'
while not os.path.exists(audio_file) or \
        not os.path.exists(video_file):
    time.sleep(0.125)
call_py.play(
    -1001234567890,
    Stream(
        AudioStream(
            InputMode.File,
            audio_file,
            AudioParameters(
                bitrate=48000,
            ),
        ),
        VideoStream(
            InputMode.File,
            video_file,
            VideoParameters(
                width=640,
                height=360,
                frame_rate=24,
            ),
        ),
    ),
)
idle()
