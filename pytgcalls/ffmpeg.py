import asyncio
import logging
import re
import shlex
import subprocess
from json import JSONDecodeError
from json import loads
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from ntgcalls import FFmpegError

from .exceptions import InvalidVideoProportion
from .exceptions import NoAudioSourceFound
from .exceptions import NoVideoSourceFound
from .types.input_stream.audio_parameters import AudioParameters
from .types.input_stream.video_parameters import VideoParameters


async def check_stream(
    ffmpeg_parameters: str,
    path: str,
    stream_parameters: Union[AudioParameters, VideoParameters],
    before_commands: List[str] = None,
    headers: Optional[Dict[str, str]] = None,
    need_image: bool = False,
):
    need_audio = isinstance(stream_parameters, AudioParameters)
    need_video = isinstance(stream_parameters, VideoParameters)

    have_video = False
    have_audio = False
    have_valid_video = False

    original_width = 0
    original_height = 0
    try:
        ffprobe = await asyncio.create_subprocess_exec(
            *tuple(
                await cleanup_commands(
                    build_command(
                        'ffprobe',
                        ffmpeg_parameters,
                        path,
                        stream_parameters,
                        before_commands,
                        headers,
                    ),
                ),
            ),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stream_list = []
        try:
            stdout, stderr = await asyncio.wait_for(
                ffprobe.communicate(),
                timeout=30,
            )
            result = loads(stdout.decode('utf-8')) or {}
            stream_list = result.get('streams', [])
        except (subprocess.TimeoutExpired, JSONDecodeError):
            pass

        for stream in stream_list:
            codec_type = stream.get('codec_type', '')
            codec_name = stream.get('codec_name', '')
            image_codecs = ['png', 'jpeg', 'jpg', 'mjpeg']
            is_valid = not need_image and codec_name in image_codecs
            if codec_type == 'video' and not is_valid:
                have_video = True
                original_width = int(stream.get('width', 0))
                original_height = int(stream.get('height', 0))
                if original_height and original_width:
                    have_valid_video = True
            elif codec_type == 'audio':
                have_audio = True

        if need_video:
            if not have_video:
                raise NoVideoSourceFound(path)
            if not have_valid_video:
                raise InvalidVideoProportion(
                    'Video proportion not found',
                )

            if isinstance(stream_parameters, VideoParameters):
                ratio = float(original_width) / original_height
                new_w = min(original_width, stream_parameters.width)
                new_h = int(new_w / ratio)

                if new_h > stream_parameters.height:
                    new_h = stream_parameters.height
                    new_w = int(new_h * ratio)

                new_w = new_w - 1 if new_w % 2 else new_w
                new_h = new_h - 1 if new_h % 2 else new_h
                stream_parameters.height = new_h
                stream_parameters.width = new_w

        if need_audio:
            if not have_audio:
                raise NoAudioSourceFound(path)
    except FileNotFoundError:
        raise FFmpegError('ffprobe not installed')


async def cleanup_commands(commands: List[str]) -> List[str]:
    try:
        proc_res = await asyncio.create_subprocess_exec(
            commands[0],
            '-h',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        result = ''
        try:
            stdout, stderr = await asyncio.wait_for(
                proc_res.communicate(),
                timeout=30,
            )
            result = stdout.decode('utf-8')
        except (subprocess.TimeoutExpired, JSONDecodeError):
            pass
        supported = re.findall(r'(-.*?)\s+', result)
        new_commands = []
        ignore_next = False

        for v in commands:
            if v[0] == '-':
                ignore_next = v not in supported
            if not ignore_next:
                new_commands += [v]
        return new_commands
    except FileNotFoundError:
        raise FFmpegError(f'{commands[0]} not installed')


def build_command(
    name: str,
    ffmpeg_parameters: str,
    path: str,
    stream_parameters: Union[AudioParameters, VideoParameters],
    before_commands: List[str] = None,
    headers: Optional[Dict[str, str]] = None,
) -> List[str]:
    command = _get_stream_params(ffmpeg_parameters)

    if isinstance(stream_parameters, VideoParameters):
        command = command['video']
    else:
        command = command['audio']

    ffmpeg_command: List = [name]

    ffmpeg_command += command['start']

    if name == 'ffprobe':
        ffmpeg_command += [
            '-v',
            'error',
            '-show_entries',
            'stream=width,height,codec_type,codec_name',
            '-of',
            'json',
        ]

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

    if name == 'ffmpeg':
        log_level = logging.getLogger().level
        if log_level == logging.DEBUG:
            ffmpeg_level = 'info'
        else:
            ffmpeg_level = 'quiet'

        ffmpeg_command += ['-v', ffmpeg_level]
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
    if name == 'ffmpeg':
        ffmpeg_command.append('pipe:1')

    return ffmpeg_command


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

    for arg in arg_names[1:]:
        for x in command_args[arg_names[0]]:
            command_args[arg][x] += command_args[arg_names[0]][x]

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
