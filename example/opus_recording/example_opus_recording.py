from pyrogram import Client
from pyrogram import filters
from pyrogram.types import Message

from pytgcalls import PyTgCalls
from pytgcalls.types import AudioQuality
from pytgcalls.types import RecordStream

app = Client(
    'py-tgcalls',
    api_id=123456789,
    api_hash='abcdef12345',
)
call_py = PyTgCalls(app)


@app.on_message(filters.regex('!record'))
async def record_handler(_: Client, message: Message):
    await call_py.record(
        message.chat.id,
        RecordStream(
            audio='record.opus',
            audio_parameters=AudioQuality.HIGH,
        ),
    )


@app.on_message(filters.regex('!stop'))
async def stop_handler(_: Client, message: Message):
    await call_py.leave_call(
        message.chat.id,
    )


call_py.run()
