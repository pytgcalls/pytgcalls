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
            have_valid_video = False
            have_audio = False
            for stream in stream_list:
                if 'Video' in stream:
                    have_video = True
                    have_valid_video = '16:9' in stream
                elif 'Audio' in stream:
                    have_audio = True
            if needed_video:
                if not have_video:
                    raise NoVideoSourceFound(path)
                if not have_valid_video:
                    raise InvalidVideoProportion()
            if not have_audio:
                raise NoAudioSourceFound(path)
        except FileNotFoundError:
            raise FFmpegNotInstalled(path)
