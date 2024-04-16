from pyrogram import Client
from pyrogram import filters
from pyrogram.types import Message

from pytgcalls import filters as fl
from pytgcalls import idle
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from pytgcalls.types import Update

app = Client(
    'py-tgcalls',
    api_id=123456789,
    api_hash='abcdef12345',
)
call_py = PyTgCalls(app)

test_stream = 'http://docs.evostream.com/sample_content/assets/' \
              'sintel1m720p.mp4'


async def custom_filter(_, client: PyTgCalls, update: Update):
    return update.chat_id in client.calls


@call_py.on_update(fl.create(custom_filter))
async def all_updates(_: PyTgCalls, update: Update):
    print(update)


@app.on_message(filters.regex('!play'))
async def play_handler(_: Client, message: Message):
    await call_py.play(
        message.chat.id,
        MediaStream(
            test_stream,
        ),
    )

call_py.start()
idle()
