from pyrogram import Client

from pytgcalls import idle
from pytgcalls import PyTgCalls
from pytgcalls.types import VideoParameters
from pytgcalls.types import VideoQuality
from pytgcalls.types.input_stream import AudioImagePiped

app = Client(
    'py-tgcalls',
    api_id=123456789,
    api_hash='abcdef12345',
)

call_py = PyTgCalls(app)
call_py.start()
audio_file = 'input.webm'
call_py.join_group_call(
    -1001234567890,
    AudioImagePiped(
        audio_file,
        'test.png',
        video_parameters=VideoParameters.from_quality(VideoQuality.HD_720p),
    ),
)
idle()
