import os
import time

from pyrogram import Client

from pytgcalls import idle
from pytgcalls import PyTgCalls
from pytgcalls import StreamType
from pytgcalls.types.input_stream import AudioParameters
from pytgcalls.types.input_stream import InputAudioStream
from pytgcalls.types.input_stream import InputStream
from pytgcalls.types.input_stream import InputVideoStream
from pytgcalls.types.input_stream import VideoParameters

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
call_py.join_group_call(
    -1001234567890,
    InputStream(
        InputAudioStream(
            audio_file,
            AudioParameters(
                bitrate=48000,
            ),
        ),
        InputVideoStream(
            video_file,
            VideoParameters(
                width=640,
                height=360,
                frame_rate=24,
            ),
        ),
    ),
    stream_type=StreamType().local_stream,
)
idle()
