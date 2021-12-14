import asyncio
import os

from pyrogram import Client
from pyrogram import filters
from pyrogram.types import Message

from pytgcalls import idle
from pytgcalls import PyTgCalls
from pytgcalls import StreamType
from pytgcalls.types import Update
from pytgcalls.types.input_stream import InputAudioStream
from pytgcalls.types.input_stream import InputStream

app = Client(
    'py-tgcalls',
    api_id=123456789,
    api_hash='abcdef12345',
)
call_py = PyTgCalls(app)


@app.on_message(filters.regex('!play'))
async def play_handler(client: Client, message: Message):
    file = '../input.raw'
    while not os.path.exists(file):
        await asyncio.sleep(0.125)
    await call_py.join_group_call(
        message.chat.id,
        InputStream(
            InputAudioStream(
                file,
            ),
        ),
        stream_type=StreamType().local_stream,
    )


@app.on_message(filters.regex('!change_stream'))
async def change_handler(client: Client, message: Message):
    file = '../input.raw'
    await call_py.change_stream(
        message.chat.id,
        InputStream(
            InputAudioStream(
                file,
            ),
        ),
    )


@app.on_message(filters.regex('!cache'))
async def cache_handler(client: Client, message: Message):
    print(call_py.cache_peer)


@app.on_message(filters.regex('!ping'))
async def ping_handler(client: Client, message: Message):
    print(call_py.ping)


@app.on_message(filters.regex('!pause'))
async def pause_handler(client: Client, message: Message):
    await call_py.pause_stream(
        message.chat.id,
    )


@app.on_message(filters.regex('!resume'))
async def resume_handler(_: Client, message: Message):
    await call_py.resume_stream(
        message.chat.id,
    )


@app.on_message(filters.regex('!stop'))
async def stop_handler(client: Client, message: Message):
    await call_py.leave_group_call(
        message.chat.id,
    )


@app.on_message(filters.regex('!change_volume'))
async def change_volume_handler(client: Client, message: Message):
    await call_py.change_volume_call(
        message.chat.id,
        50,
    )


@call_py.on_kicked()
async def kicked_handler(client: PyTgCalls, chat_id: int):
    print(f'Kicked from {chat_id}')


@call_py.on_raw_update()
async def raw_handler(client: PyTgCalls, update: Update):
    print(update)


@call_py.on_stream_end()
async def stream_end_handler(client: PyTgCalls, update: Update):
    print(f'Stream ended in {update.chat_id}', update)


@call_py.on_participants_change()
async def participant_handler(client: PyTgCalls, update: Update):
    print(update)

call_py.start()
idle()
