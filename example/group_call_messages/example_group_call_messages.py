from pyrogram import Client
from pyrogram import filters
from pyrogram.types import Message

from pytgcalls import PyTgCalls
from pytgcalls import filters as fl
from pytgcalls.types import GroupCallMessage
from pytgcalls.types import UpdatedGroupCallMessage

app = Client(
    'py-tgcalls',
    api_id=123456789,
    api_hash='abcdef12345',
)
call_py = PyTgCalls(app)


@app.on_message(filters.regex('!play'))
async def play_handler(_: Client, message: Message):
    await call_py.play(
        message.chat.id,
        'http://docs.evostream.com/sample_content/assets/sintel1m720p.mp4',
    )
    await call_py.send_message(
        message.chat.id,
        '<b>Now playing:</b> Lena Raine - Resurrections 🍓 '
        '<tg-spoiler>Madeline finally hatched 🐣</tg-spoiler>',
    )


@call_py.on_update(fl.call_message(GroupCallMessage.Action.RECEIVED))
async def message_handler(_: PyTgCalls, update: UpdatedGroupCallMessage):
    message = update.message
    print(f'{message.sender_id} in {update.chat_id}: {message.html}')
    if message.text == '!ping':
        await call_py.send_message(update.chat_id, '<b>Pong!</b> 🏓')
    elif message.text == '!clear':
        await call_py.delete_messages(update.chat_id, message.message_id)


@call_py.on_update(fl.call_message(GroupCallMessage.Action.DELETED))
async def deleted_handler(_: PyTgCalls, update: UpdatedGroupCallMessage):
    print(f'Message {update.message_id} deleted in {update.chat_id}')


call_py.run()
