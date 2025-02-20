from ai_model import AIModel
from pyrogram import Client
from pyrogram import idle

from pytgcalls import filters
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioQuality
from pytgcalls.types import Device
from pytgcalls.types import Direction
from pytgcalls.types import RecordStream
from pytgcalls.types import StreamFrame

AUDIO_QUALITY = AudioQuality.HIGH

model = AIModel(AUDIO_QUALITY)
app = Client('py-tgcalls', api_id=123456789, api_hash='abcdef12345')
call_py = PyTgCalls(app)
call_py.start()
call_py.record(
    'username',
    RecordStream(
        True,
        AUDIO_QUALITY,
    ),
)


@call_py.on_update(filters.stream_frame(Direction.INCOMING, Device.MICROPHONE))
async def audio_data(_: PyTgCalls, update: StreamFrame):
    stt = model.transcribe(update.frame)
    if stt:
        print(stt, flush=True)

idle()
