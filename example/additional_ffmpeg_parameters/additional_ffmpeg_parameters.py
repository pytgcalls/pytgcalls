from pyrogram import Client

from pytgcalls import idle
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioQuality
from pytgcalls.types import MediaStream
from pytgcalls.types import VideoQuality
from pytgcalls.types.raw import AudioParameters
from pytgcalls.types.raw import VideoParameters

app = Client(
    'py-tgcalls',
    api_id=123456789,
    api_hash='abcdef12345',
)

call_py = PyTgCalls(app)
call_py.start()
remote = 'http://docs.evostream.com/sample_content/assets/sintel1m720p.mp4'
call_py.join_group_call(
    -1001234567890,
    MediaStream(
        remote,
        AudioParameters.from_quality(AudioQuality.HIGH),
        VideoParameters.from_quality(VideoQuality.HD_720p),

        # You can add --video or --audio to the ffmpeg
        # command line to specify to what you want to add these parameters
        ffmpeg_parameters='EVERYTHING BEFORE THE INPUT (-i) '
                          '-atmid '
                          'EVERYTHING AFTER THE INPUT (-i) '
                          '-atend '
                          'EVERYTHING AFTER ALL ARGUMENTS',
    ),
)
idle()
