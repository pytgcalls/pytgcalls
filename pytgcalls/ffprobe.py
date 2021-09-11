import asyncio
import re
import subprocess

from .exceptions import FFmpegNotInstalled
from .exceptions import InvalidVideoProportion
from .exceptions import NoAudioSourceFound
from .exceptions import NoVideoSourceFound


class FFprobe:
    @staticmethod
    async def check_file(
        path: str,
        needed_video=False,
    ):
        try:
            ffprobe = await asyncio.create_subprocess_exec(
                'ffprobe',
                path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            result = ''
            try:
                while True:
                    try:
                        if ffprobe.stderr is None:
                            break
                        out = (await ffprobe.stderr.read())
                        result += out.decode()
                        if not out:
                            break
                    except TimeoutError:
                        pass
            except KeyboardInterrupt:
                pass
            stream_list = re.compile(r'Stream #.*:.*').findall(result)
            have_video = False
            have_audio = False
            have_valid_video = False
            original_width = 0
            original_height = 0
            for stream in stream_list:
                if 'Video' in stream:
                    have_video = True
                    video_params = re.compile(
                        r'\d{2,5}x\d{2,5}',
                    ).findall(stream)
                    if video_params:
                        have_valid_video = True
                        original_width = int(video_params[0].split('x')[0])
                        original_height = int(video_params[0].split('x')[1])
                elif 'Audio' in stream:
                    have_audio = True
            if needed_video:
                if not have_video:
                    raise NoVideoSourceFound(path)
                if not have_valid_video:
                    raise InvalidVideoProportion(
                        'Video proportion not found',
                    )
            if not have_audio:
                raise NoAudioSourceFound(path)
            if have_video:
                return original_width, original_height
        except FileNotFoundError:
            raise FFmpegNotInstalled(path)
