import shlex
from typing import List, Union

from .types.input_stream.audio_parameters import AudioParameters
from .types.input_stream.video_parameters import VideoParameters

def build_ffmpeg_command(
    ffmpeg_parameters: str,
    path: str,
    stream_type: str,
    stream_parameters: Union[AudioParameters, VideoParameters],
) -> str:
    command = _get_stream_params(ffmpeg_parameters)

    if stream_type == 'video' or stream_type == 'image':
        command = command['video']
    else:
        command = command['audio']

    ffmpeg_command: List = ['ffmpeg']

    ffmpeg_command += command['start']

    if stream_type == 'image':
        stream_parameters.frame_rate = 1
        ffmpeg_command += [
            '-loop',
            1,
            '-framerate',
            stream_parameters.frame_rate,
        ]

    ffmpeg_command += [
        '-i',
        path,
    ]
    ffmpeg_command += command['mid']
    ffmpeg_command.append('-f')

    if stream_type == 'video' or stream_type == 'image':
        ffmpeg_command += [
            'rawvideo',
            '-r',
            stream_parameters.frame_rate,
            '-pix_fmt',
            'yuv420p',
            '-vf',
            f'scale={stream_parameters.width}:{stream_parameters.height}'
        ]
    else:
        ffmpeg_command += [
            's16le',
            '-ac',
            stream_parameters.channels,
            '-ar',
            stream_parameters.bitrate
        ]

    ffmpeg_command += command['end']
    ffmpeg_command.append('pipe:1')

    return ' '.join([
        str(el) if isinstance(el, int) else el
        for el in ffmpeg_command
    ])


def _get_stream_params(command: str):
    arg_names = ['base', 'audio', 'video']
    command_args: dict = {arg: [] for arg in arg_names}
    current_arg = arg_names[0]

    for part in shlex.split(command):
        arg_name = part[2:]
        if arg_name in arg_names:
            current_arg = arg_name
        else:
            command_args[current_arg].append(part)
    command_args = {
        command: _extract_stream_params(command_args[command])
        for command in command_args
    }

    del command_args[arg_names[0]]

    return command_args


def _extract_stream_params(command: list[str]):
    arg_names = ['start', 'mid', 'end']
    command_args: dict = {arg: [] for arg in arg_names}
    current_arg = arg_names[0]

    for part in command:
        arg_name = part[3:]
        if arg_name in arg_names:
            current_arg = arg_name
        else:
            command_args[current_arg].append(part)

    return command_args
