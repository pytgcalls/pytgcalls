from pyrogram import Client, idle
from pytgcalls import PyTgCalls, filters
from pytgcalls.types import Device, Direction, RecordStream, AudioQuality
from pytgcalls.types import StreamFrame
from ai_model import AIModel

AUDIO_QUALITY = AudioQuality.HIGH

model = AIModel(AUDIO_QUALITY)
app = Client("py-tgcalls", api_id=123456789, api_hash="abcdef12345")
call_py = PyTgCalls(app)
call_py.start()
call_py.record(
    "username",
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
