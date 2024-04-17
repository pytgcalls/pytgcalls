from pyrogram import Client
from pyrogram import filters
from pyrogram.types import Message

from pytgcalls import compose
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream

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

test_stream = 'http://docs.evostream.com/sample_content/assets/' \
              'sintel1m720p.mp4'

# You can enter an unlimited number of PyTgCalls clients
call_py = PyTgCalls(app)
call_py2 = PyTgCalls(app2)


@app.on_message(filters.regex('!p1'))
async def play_handler(_: Client, message: Message):
    await call_py.play(
        message.chat.id,
        MediaStream(
            test_stream,
        ),
    )


@app.on_message(filters.regex('!p2'))
async def play_handler2(_: Client, message: Message):
    await call_py2.play(
        message.chat.id,
        MediaStream(
            test_stream,
        ),
    )


@app.on_message(filters.regex('!s1'))
async def stop_handler(_: Client, message: Message):
    await call_py.leave_call(
        message.chat.id,
    )


@app.on_message(filters.regex('!s2'))
async def stop_handler2(_: Client, message: Message):
    await call_py2.leave_call(
        message.chat.id,
    )

compose([app, app2])
