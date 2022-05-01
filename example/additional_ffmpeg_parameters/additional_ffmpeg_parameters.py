from pyrogram import Client

from pytgcalls import idle
from pytgcalls import PyTgCalls
from pytgcalls import StreamType
from pytgcalls.types.input_stream import AudioVideoPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio
from pytgcalls.types.input_stream.quality import HighQualityVideo

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
    AudioVideoPiped(
        remote,
        HighQualityAudio(),
        HighQualityVideo(),

        # You can add --video or --audio to the ffmpeg
        # command line to specify to what you want to add these parameters
        additional_ffmpeg_parameters='EVERYTHING BEFORE THE INPUT (-i) '
                                     '-atmid '
                                     'EVERYTHING AFTER THE INPUT (-i) '
                                     '-atend '
                                     'EVERYTHING AFTER ALL ARGUMENTS',
    ),
    stream_type=StreamType().pulse_stream,
)
idle()
