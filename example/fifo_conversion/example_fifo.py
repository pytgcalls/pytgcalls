import asyncio
import os
import time

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
    @app.on_message(filters.regex('!p1'))
    async def play_handler(client: Client, message: Message):
        file = 'input.mp3'
        output_file = 'input_fifo.raw'
        os.mkfifo(output_file)
        await asyncio.create_subprocess_shell(
            cmd=(
                'ffmpeg '
                '-y -i '
                f'{file} '
                '-f s16le '
                '-ac 1 '
                '-ar 48000 '
                '-acodec pcm_s16le '
                f'{output_file}'
            ),
            stdin=asyncio.subprocess.PIPE,
        )
        while not os.path.exists(output_file):
            time.sleep(0.125)
        call_py.join_group_call(
            message.chat.id,
            output_file,
            stream_type=StreamType().pulse_stream,
        )
    call_py.run()
