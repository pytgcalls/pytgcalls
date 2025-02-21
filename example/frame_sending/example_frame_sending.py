import time

from pyrogram import Client

from pytgcalls import idle
from pytgcalls import PyTgCalls
from pytgcalls.types import Device
from pytgcalls.types import ExternalMedia
from pytgcalls.types import MediaStream
from pytgcalls.types.raw import AudioParameters

app = Client(
    'py-tgcalls',
    api_id=123456789,
    api_hash='abcdef12345',
)
call_py = PyTgCalls(app)
call_py.start()

chat_id = -1001234567890
audio_file = 'audio.raw'
audio_parameters = AudioParameters(
    bitrate=48000,
    channels=2,
)

call_py.play(
    chat_id,
    MediaStream(
        ExternalMedia.AUDIO,
        audio_parameters,
    ),
)

with open(audio_file, 'rb') as f:
    # Should be sent in PCM16L format
    chunk_size = audio_parameters.bitrate * \
        16 // 8 // 100 * audio_parameters.channels
    while chunk := f.read(chunk_size):
        call_py.send_frame(
            chat_id,
            Device.MICROPHONE,
            chunk,
        )
        time.sleep(0.01)
idle()
