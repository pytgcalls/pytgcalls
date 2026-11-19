from pyrogram import Client
from pyrogram import filters
from pyrogram.types import Message

from pytgcalls import PyTgCalls
from pytgcalls.types import AudioQuality
from pytgcalls.types import MediaStream
from pytgcalls.types.raw import AudioParameters

app = Client(
    'py-tgcalls',
    api_id=123456789,
    api_hash='abcdef12345',
)
call_py = PyTgCalls(app)
test_stream = (
    'http://docs.evostream.com/sample_content/assets/sintel1m720p.mp4'
)


@app.on_message(filters.regex('!studio'))
async def studio_handler(_: Client, message: Message):
    await call_py.play(
        message.chat.id,
        MediaStream(
            test_stream,
            audio_parameters=AudioQuality.STUDIO,
        ),
    )


@app.on_message(filters.regex('!voice'))
async def voice_handler(_: Client, message: Message):
    await call_py.play(
        message.chat.id,
        MediaStream(
            test_stream,
            audio_parameters=AudioQuality.VOICE,
        ),
    )


@app.on_message(filters.regex('!custom'))
async def custom_handler(_: Client, message: Message):
    await call_py.play(
        message.chat.id,
        MediaStream(
            test_stream,
            audio_parameters=AudioParameters(
                sample_rate=48000,
                channels=2,
                bitrate=160000,
            ),
        ),
    )


call_py.run()
