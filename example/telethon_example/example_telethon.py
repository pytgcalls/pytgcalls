from telethon import TelegramClient

from pytgcalls import idle
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream

app = TelegramClient(
    'py-tgcalls',
    api_id=123456789,
    api_hash='abcdef12345',
)

call_py = PyTgCalls(app)
call_py.start()
test_stream = 'http://docs.evostream.com/sample_content/assets/' \
              'sintel1m720p.mp4'
call_py.play(
    -1001234567890,
    MediaStream(
        test_stream,
    ),
)
idle()
