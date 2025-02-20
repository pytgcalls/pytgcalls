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

app = Client(
    'py-tgcalls', 
    api_id=12345, 
    api_hash="0123456789abcdef0123456789abcdef",
)

call_py = PyTgCalls(app)
chat_id = 1234567890
call_py.start()
call_py.record(
    chat_id,
    RecordStream(
        True,
        AUDIO_QUALITY,
    ),
)

@call_py.on_update(
    filters.stream_frame(
        Direction.INCOMING, 
        Device.MICROPHONE,
    ),
)
async def audio_data(_: PyTgCalls, update: StreamFrame):
    stt = model.transcribe(update.frame)
    if stt:
        print(stt, flush=True)

idle()
