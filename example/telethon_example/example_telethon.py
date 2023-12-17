from telethon import TelegramClient

from pytgcalls import PyTgCalls
from pytgcalls import idle
from pytgcalls.types import AudioVideoPiped

app = TelegramClient(
    'py-tgcalls',
    api_id=123456789,
    api_hash='abcdef12345',
)

call_py = PyTgCalls(app)
call_py.start()
test_stream = 'http://docs.evostream.com/sample_content/assets/sintel1m720p.mp4'
call_py.join_group_call(
    -1001234567890,
    AudioVideoPiped(
        test_stream
    ),
)
idle()
