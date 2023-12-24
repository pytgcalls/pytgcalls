import asyncio

from pyrogram import Client

from pytgcalls import idle
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioParameters
from pytgcalls.types import AudioQuality
from pytgcalls.types import VideoParameters
from pytgcalls.types import VideoQuality
from pytgcalls.types.input_stream import AudioVideoPiped


# USE THIS IF YOU WANT SYNC WAY
def get_youtube_stream() -> (str, str):
    # USE THIS IF YOU WANT ASYNC WAY
    async def run_async() -> (str, str):
        proc = await asyncio.create_subprocess_exec(
            'yt-dlp',
            '-g',
            '-f',
            # CHANGE THIS BASED ON WHAT YOU WANT
            'bestvideo+bestaudio/best',
            'https://www.youtube.com/watch?v=msiLgFkXvD8',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        data = stdout.decode().split('\n')
        return data[0], data[1]
    return asyncio.get_event_loop().run_until_complete(run_async())


app = Client(
    'py-tgcalls',
    api_id=123456789,
    api_hash='abcdef12345',
)

call_py = PyTgCalls(app)
call_py.start()
remote = get_youtube_stream()
call_py.join_group_call(
    -1001234567890,
    AudioVideoPiped(
        remote[0],
        AudioParameters.from_quality(AudioQuality.HIGH),
        VideoParameters.from_quality(VideoQuality.HD_720p),
        audio_path=remote[1],
    ),
)
idle()
