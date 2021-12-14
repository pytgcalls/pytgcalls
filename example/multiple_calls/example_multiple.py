import asyncio
import os
import time

from pyrogram import Client
from pyrogram import filters
from pyrogram.types import Message

from pytgcalls import idle
from pytgcalls import PyTgCalls
from pytgcalls import StreamType
from pytgcalls.types.input_stream import InputAudioStream
from pytgcalls.types.input_stream import InputStream

app = Client(
    'py-tgcalls',
    api_id=123456789,
    api_hash='abcdef12345',
)
app2 = Client(
    'py-tgcalls',
    api_id=123456789,
    api_hash='abcdef12345',
)

# You can enter an unlimited number of PyTgCalls clients
call_py = PyTgCalls(app)
call_py2 = PyTgCalls(app2)


@app.on_message(filters.regex('!p1'))
async def play_handler(client: Client, message: Message):
    file = '../input.raw'
    while not os.path.exists(file):
        time.sleep(0.125)
    await call_py.join_group_call(
        message.chat.id,
        InputStream(
            InputAudioStream(
                file,
            ),
        ),
        stream_type=StreamType().local_stream,
    )


@app.on_message(filters.regex('!p2'))
async def play_handler2(client: Client, message: Message):
    file = '../input.raw'
    while not os.path.exists(file):
        await asyncio.sleep(0.125)
    await call_py2.join_group_call(
        message.chat.id,
        InputStream(
            InputAudioStream(
                file,
            ),
        ),
        stream_type=StreamType().local_stream,
    )


@app.on_message(filters.regex('!s1'))
async def stop_handler(client: Client, message: Message):
    await call_py.leave_group_call(
        message.chat.id,
    )


@app.on_message(filters.regex('!s2'))
async def stop_handler2(client: Client, message: Message):
    await call_py2.leave_group_call(
        message.chat.id,
    )

call_py.start()
call_py2.start()
idle()
