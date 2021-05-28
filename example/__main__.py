import asyncio
import os

from pyrogram import Client
from pyrogram import filters
from pyrogram.types import Message

from pytgcalls import PyLogs
from pytgcalls import PyTgCalls
from pytgcalls import StreamType

app = Client(
    'py-tgcalls',
    api_id=123456789,
    api_hash='abcdef12345',
)
call_py = PyTgCalls(
    app,
    log_mode=PyLogs.ultra_verbose,
)
if __name__ == '__main__':
    @app.on_message(filters.regex('!play'))
    async def play_handler(client: Client, message: Message):
        file = 'input.raw'
        while not os.path.exists(file):
            await asyncio.sleep(0.125)
        call_py.join_group_call(
            message.chat.id,
            file,
            stream_type=StreamType().local_stream,
        )

    @app.on_message(filters.regex('!change_stream'))
    async def change_handler(client: Client, message: Message):
        file = 'input.raw'
        call_py.change_stream(
            message.chat.id,
            file,
        )

    @app.on_message(filters.regex('!cache'))
    async def cache_handler(client: Client, message: Message):
        print(call_py.get_cache_peer())

    @app.on_message(filters.regex('!pause'))
    async def pause_handler(client: Client, message: Message):
        call_py.pause_stream(
            message.chat.id,
        )

    @app.on_message(filters.regex('!resume'))
    async def resume_handler(_: Client, message: Message):
        call_py.resume_stream(
            message.chat.id,
        )

    @app.on_message(filters.regex('!stop'))
    async def stop_handler(client: Client, message: Message):
        call_py.leave_group_call(
            message.chat.id,
        )

    @app.on_message(filters.regex('!change_volume'))
    async def change_volume_handler(client: Client, message: Message):
        call_py.change_volume_call(
            message.chat.id,
            50,
        )

    @call_py.on_kicked()
    async def kicked_handler(chat_id: int):
        print(f'Kicked from {chat_id}')

    @call_py.on_raw_update()
    async def raw_handler(json):
        print(json)

    @call_py.on_stream_end()
    async def stream_end_handler(chat_id: int):
        print(f'Stream endend in {chat_id}')

    call_py.run()
