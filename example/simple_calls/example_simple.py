from pyrogram import Client
from pyrogram import filters
from pyrogram.types import Message

from pytgcalls import PyTgCalls
from pytgcalls import idle
from pytgcalls.types import Update, AudioVideoPiped

app = Client(
    'py-tgcalls',
    api_id=123456789,
    api_hash='abcdef12345',
)
call_py = PyTgCalls(app)

test_stream = 'http://docs.evostream.com/sample_content/assets/sintel1m720p.mp4'


@app.on_message(filters.regex('!play'))
async def play_handler(_: Client, message: Message):
    await call_py.join_group_call(
        message.chat.id,
        AudioVideoPiped(
            test_stream
        ),
    )


@app.on_message(filters.regex('!change_stream'))
async def change_handler(_: Client, message: Message):
    await call_py.change_stream(
        message.chat.id,
        AudioVideoPiped(
            test_stream
        ),
    )


@app.on_message(filters.regex('!cache'))
async def cache_handler(_: Client, _m: Message):
    print(call_py.cache_peer)


@app.on_message(filters.regex('!ping'))
async def ping_handler(_: Client, _m: Message):
    print(call_py.ping)


@app.on_message(filters.regex('!pause'))
async def pause_handler(_: Client, message: Message):
    await call_py.pause_stream(
        message.chat.id,
    )


@app.on_message(filters.regex('!resume'))
async def resume_handler(_: Client, message: Message):
    await call_py.resume_stream(
        message.chat.id,
    )


@app.on_message(filters.regex('!stop'))
async def stop_handler(_: Client, message: Message):
    await call_py.leave_group_call(
        message.chat.id,
    )


@app.on_message(filters.regex('!change_volume'))
async def change_volume_handler(_: Client, message: Message):
    await call_py.change_volume_call(
        message.chat.id,
        50,
    )


@app.on_message(filters.regex('!status'))
async def get_play_status(client: Client, message: Message):
    await client.send_message(
        message.chat.id,
        f'Current seconds {await call_py.played_time(message.chat.id)}',
    )


@call_py.on_kicked()
async def kicked_handler(_: PyTgCalls, chat_id: int):
    print(f'Kicked from {chat_id}')


@call_py.on_raw_update()
async def raw_handler(_: PyTgCalls, update: Update):
    print(update)


@call_py.on_stream_end()
async def stream_end_handler(_: PyTgCalls, update: Update):
    print(f'Stream ended in {update.chat_id}', update)


@call_py.on_participants_change()
async def participant_handler(_: PyTgCalls, update: Update):
    print(update)

call_py.start()
idle()
