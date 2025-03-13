import numpy as np
from pyrogram import Client

from pytgcalls import filters
from pytgcalls import idle
from pytgcalls import PyTgCalls
from pytgcalls.types import Device
from pytgcalls.types import Direction
from pytgcalls.types import ExternalMedia
from pytgcalls.types import MediaStream
from pytgcalls.types import RecordStream
from pytgcalls.types import StreamFrames
from pytgcalls.types.raw import AudioParameters

app = Client(
    'py-tgcalls',
    api_id=12345,
    api_hash='0123456789abcdef0123456789abcdef',
)
call_py = PyTgCalls(app)
call_py.start()

AUDIO_PARAMETERS = AudioParameters(
    bitrate=48000,
    channels=2,
)
chat_ids = [
    -1001962986321,
    -1001398466177,
]
for chat_id in chat_ids:
    call_py.play(
        chat_id,
        MediaStream(
            ExternalMedia.AUDIO,
            AUDIO_PARAMETERS,
        ),
    )
    call_py.record(
        chat_id,
        RecordStream(
            True,
            AUDIO_PARAMETERS,
        ),
    )


@call_py.on_update(
    filters.stream_frame(
        Direction.INCOMING,
        Device.MICROPHONE,
    ),
)
async def audio_data(_: PyTgCalls, update: StreamFrames):
    # Mix all incoming audio data and send it to
    # all chats except the one it came from
    forward_chat_ids = [x for x in chat_ids if x != update.chat_id]
    mixed_output = np.zeros(
        len(update.frames[0].frame) // 2,
        dtype=np.int16,
    )
    for frame_data in update.frames:
        source_samples = np.frombuffer(frame_data.frame, dtype=np.int16)
        mixed_output[:len(source_samples)] += source_samples

    mixed_output //= max(len(update.frames), 1)
    mixed_output = np.clip(mixed_output, -32768, 32767)
    for f_chat_id in forward_chat_ids:
        await call_py.send_frame(
            f_chat_id,
            Device.MICROPHONE,
            mixed_output.tobytes(),
        )

idle()
