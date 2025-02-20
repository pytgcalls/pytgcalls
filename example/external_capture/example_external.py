from pyrogram import Client
from pyrogram import filters
from pyrogram.types import Message

from pytgcalls import filters as fl
from pytgcalls import idle
from pytgcalls import PyTgCalls
from pytgcalls.types import Device
from pytgcalls.types import RecordStream
from pytgcalls.types.raw import AudioParameters

app = Client(
    'py-tgcalls',
    api_id=123456789,
    api_hash='abcdef12345',
)
call_py = PyTgCalls(app)


@app.on_message(filters.regex('!record'))
async def play_handler(_: Client, message: Message):
    await call_py.record(
        message.chat.id,
        RecordStream(
            audio=True,
            audio_parameters=AudioParameters(
                bitrate=48000,
                channels=2,
            ),
            camera=True,
            screen=True,
        ),
    )


@call_py.on_update(fl.stream_frame())
async def stream_frame_handler(_, update):
    # Receive all kind of stream frame
    print(update)


@call_py.on_update(
    fl.stream_frame(
        devices=Device.MICROPHONE | Device.SPEAKER,
    ),
)
async def stream_audio_frame_handler(_, update):
    # Receive only all kind of audio stream frame
    print(update)

call_py.start()
idle()
