import asyncio
import json
import subprocess
from json import JSONDecodeError
from typing import Dict
from typing import List
from typing import Optional

from .exceptions import FFmpegNotInstalled
from .exceptions import InvalidVideoProportion
from .exceptions import NoAudioSourceFound
from .exceptions import NoVideoSourceFound
from .types.input_stream.video_tools import check_support


class FFprobe:
    @staticmethod
    def ffmpeg_headers(
        headers: Optional[Dict[str, str]] = None,
    ):
        ffmpeg_params: List[str] = []
        if headers is not None:
            ffmpeg_params.append('-headers')
            built_header = ''
            for i in headers:
                built_header += f'{i}: {headers[i]}\r\n'
            ffmpeg_params.append(built_header)
        return ':_cmd_:'.join(
            ffmpeg_params,
        )

    @staticmethod
    async def check_file(
        path: str,
        needed_audio=False,
        needed_video=False,
        needed_image=False,
        headers: Optional[Dict[str, str]] = None,
    ):
        ffmpeg_params: List[str] = []
        have_header = False
        if headers is not None and \
                check_support(path):
            ffmpeg_params.append('-headers')
            built_header = ''
            have_header = True
            for i in headers:
                built_header += f'{i}: {headers[i]}\r\n'
            ffmpeg_params.append(built_header)
        try:
            ffprobe = await asyncio.create_subprocess_exec(
                'ffprobe',
                '-v',
                'error',
                '-show_entries',
                'stream=width,height,codec_type,codec_name',
                '-of',
                'json',
                path,
                *tuple(ffmpeg_params),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stream_list = []
            try:
                stdout, stderr = await asyncio.wait_for(
                    ffprobe.communicate(),
                    timeout=30,
                )
                result = json.loads(stdout.decode('utf-8')) or {}
                stream_list = result.get('streams', [])
            except (subprocess.TimeoutExpired, JSONDecodeError):
                pass
            have_video = False
            have_audio = False
            have_valid_video = False
            original_width = 0
            original_height = 0
            for stream in stream_list:
                codec_type = stream.get('codec_type', '')
                codec_name = stream.get('codec_name', '')
                image_codecs = ['png', 'jpeg', 'jpg', 'mjpeg']
                is_valid = not needed_image and codec_name in image_codecs
                if codec_type == 'video' and not is_valid:
                    have_video = True
                    original_width = int(stream.get('width', 0))
                    original_height = int(stream.get('height', 0))
                    if original_height and original_width:
                        have_valid_video = True
                elif codec_type == 'audio':
                    have_audio = True
            if needed_video:
                if not have_video:
                    raise NoVideoSourceFound(path)
                if not have_valid_video:
                    raise InvalidVideoProportion(
                        'Video proportion not found',
                    )
            if needed_audio:
                if not have_audio:
                    raise NoAudioSourceFound(path)
                if not needed_video:
                    return have_header
            if have_video:
                return original_width, original_height, have_header
        except FileNotFoundError:
            raise FFmpegNotInstalled(path)
