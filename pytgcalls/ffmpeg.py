import asyncio
import logging
import os.path
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

from .exceptions import ImageSourceFound
from .exceptions import InvalidVideoProportion
from .exceptions import LiveStreamFound
from .exceptions import NoAudioSourceFound
from .exceptions import NoVideoSourceFound
from .types.raw import AudioParameters
from .types.raw import VideoParameters


async def check_stream(
    ffmpeg_parameters: Optional[str],
    path: str,
    stream_parameters: Union[AudioParameters, VideoParameters],
    before_commands: Optional[List[str]] = None,
    headers: Optional[Dict[str, str]] = None,
):
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
                        False,
                    ),
                ),
            ),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except FileNotFoundError:
        raise FFmpegError('ffprobe not installed')

    stream_list = []
    format_content = []
    try:
        stdout, stderr = await asyncio.wait_for(
            ffprobe.communicate(),
            timeout=30,
        )
        result = loads(stdout.decode('utf-8')) or {}
        stream_list = result.get('streams', [])
        format_content = result.get('format', [])
        if 'No such file' in stderr.decode('utf-8'):
            raise FileNotFoundError()
    except (subprocess.TimeoutExpired, JSONDecodeError):
        pass

    have_video = False
    is_image = False
    have_audio = False
    have_valid_video = False

    original_width, original_height = 0, 0

    for stream in stream_list:
        codec_type = stream.get('codec_type', '')
        codec_name = stream.get('codec_name', '')
        image_codecs = ['png', 'jpeg', 'jpg', 'mjpeg']
        if codec_type == 'video':
            is_image = codec_name in image_codecs
            have_video = True
            original_width = int(stream.get('width', 0))
            original_height = int(stream.get('height', 0))
            if original_height and original_width:
                have_valid_video = True
        elif codec_type == 'audio':
            have_audio = True

    if isinstance(stream_parameters, VideoParameters):
        if not have_video:
            raise NoVideoSourceFound(path)
        if not have_valid_video:
            raise InvalidVideoProportion(
                'Video proportion not found',
            )

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
        if is_image:
            stream_parameters.frame_rate = 1
            raise ImageSourceFound(path)

    if isinstance(stream_parameters, AudioParameters) and not have_audio:
        raise NoAudioSourceFound(path)

    if 'duration' not in format_content:
        raise LiveStreamFound(path)


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
            stdout, _ = await asyncio.wait_for(
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
            if len(v) > 0:
                if v[0] == '-':
                    ignore_next = v not in supported
                if not ignore_next:
                    new_commands += [v]
        return new_commands
    except FileNotFoundError:
        raise FFmpegError(f'{commands[0]} not installed')


def build_command(
    name: str,
    ffmpeg_parameters: Optional[str],
    path: Optional[str],
    stream_parameters: Union[AudioParameters, VideoParameters],
    before_commands: Optional[List[str]] = None,
    headers: Optional[Dict[str, str]] = None,
    is_livestream: bool = False,
) -> List[str]:
    if not path:
        return []
    command = _get_stream_params(ffmpeg_parameters)

    if isinstance(stream_parameters, VideoParameters):
        command = command['video']
    else:
        command = command['audio']

    ffmpeg_command: List = [name]

    ffmpeg_command += command['start']

    if not os.path.exists(path) \
            and not is_livestream\
            and name == 'ffmpeg':
        ffmpeg_command += [
            '-reconnect',
            '1',
            '-reconnect_at_eof',
            '1',
            '-reconnect_streamed',
            '1',
            '-reconnect_delay_max',
            '2',
        ]

    if name == 'ffprobe':
        ffmpeg_command += [
            '-v',
            'error',
            '-show_entries',
            'stream=width,height,codec_type,codec_name',
            '-show_format',
            '-of',
            'json',
        ]

    if before_commands:
        ffmpeg_command += before_commands

    if headers is not None:
        for i in headers:
            ffmpeg_command.append('-headers')
            ffmpeg_command.append(f'"{i}: {headers[i]}"')

    ffmpeg_command += [
        '-nostdin',
        '-i',
        f'"{path}"' if name == 'ffmpeg' else path,
    ]
    ffmpeg_command += command['mid']

    if name == 'ffmpeg':
        ffmpeg_command += _build_ffmpeg_options(stream_parameters)

    ffmpeg_command += command['end']
    if name == 'ffmpeg':
        ffmpeg_command.append('pipe:1')

    return ffmpeg_command


def _get_stream_params(command: Optional[str]):
    arg_names = ['base', 'audio', 'video']
    command_args: Dict = {arg: [] for arg in arg_names}
    current_arg = arg_names[0]

    if command:
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


def _build_ffmpeg_options(
        stream_parameters: Union[AudioParameters, VideoParameters],
) -> List[str]:
    log_level = logging.getLogger().level
    ffmpeg_level = 'info' if log_level == logging.DEBUG else 'quiet'

    options = ['-v', ffmpeg_level, '-f']

    if isinstance(stream_parameters, AudioParameters):
        options.extend([
            's16le',
            '-ac', str(stream_parameters.channels),
            '-ar', str(stream_parameters.bitrate),
        ])
    elif isinstance(stream_parameters, VideoParameters):
        options.extend([
            'rawvideo',
            '-r', str(stream_parameters.frame_rate),
            '-pix_fmt', 'yuv420p',
            '-vf',
            f'scale={stream_parameters.width}:{stream_parameters.height}',
        ])

    return options
