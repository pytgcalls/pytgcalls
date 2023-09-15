import shlex
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from .types.input_stream.audio_parameters import AudioParameters
from .types.input_stream.video_parameters import VideoParameters


def build_ffmpeg_command(
    ffmpeg_parameters: str,
    path: str,
    stream_parameters: Union[AudioParameters, VideoParameters],
    before_commands: List[str] = None,
    headers: Optional[Dict[str, str]] = None,
) -> str:
    command = _get_stream_params(ffmpeg_parameters)

    if isinstance(stream_parameters, VideoParameters):
        command = command['video']
    else:
        command = command['audio']

    ffmpeg_command: List = ['ffmpeg']

    ffmpeg_command += command['start']

    if before_commands:
        ffmpeg_command += before_commands

    if headers is not None:
        ffmpeg_command.append('-headers')
        built_header = '"'
        for i in headers:
            built_header += f'{i}: {headers[i]}\r\n'

        ffmpeg_command.append(built_header + '"')

    ffmpeg_command += [
        '-i',
        path,
    ]
    ffmpeg_command += command['mid']
    ffmpeg_command.append('-f')

    if isinstance(stream_parameters, VideoParameters):
        ffmpeg_command += [
            'rawvideo',
            '-r',
            str(stream_parameters.frame_rate),
            '-pix_fmt',
            'yuv420p',
            '-vf',
            f'scale={stream_parameters.width}:{stream_parameters.height}',
        ]
    else:
        ffmpeg_command += [
            's16le',
            '-ac',
            str(stream_parameters.channels),
            '-ar',
            str(stream_parameters.bitrate),
        ]

    ffmpeg_command += command['end']
    ffmpeg_command.append('pipe:1')

    return ' '.join(ffmpeg_command)


def _get_stream_params(command: str):
    arg_names = ['base', 'audio', 'video']
    command_args: Dict = {arg: [] for arg in arg_names}
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


def _extract_stream_params(command: List[str]):
    arg_names = ['start', 'mid', 'end']
    command_args: Dict = {arg: [] for arg in arg_names}
    current_arg = arg_names[0]

    for part in command:
        arg_name = part[3:]
        if arg_name in arg_names:
            current_arg = arg_name
        else:
            command_args[current_arg].append(part)

    return command_args
