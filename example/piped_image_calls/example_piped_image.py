from pyrogram import Client

from pytgcalls import idle
from pytgcalls import PyTgCalls
from pytgcalls import StreamType
from pytgcalls.types.input_stream import AudioImagePiped
from pytgcalls.types.input_stream.quality import HighQualityVideo

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
        video_parameters=HighQualityVideo(),
    ),
    stream_type=StreamType().pulse_stream,
)
idle()
