import asyncio
import re
from typing import Tuple

from .exceptions import YtDlpError
from .types.raw import VideoParameters


class YtDlp:
    YOUTUBE_REGX = re.compile(
        r'^((?:https?:)?//)?((?:www|m)\.)?'
        r'(youtube(-nocookie)?\.com|youtu.be)'
        r'(/(?:[\w\-]+\?v=|embed/|live/|v/)?)'
        r'([\w\-]+)(\S+)?$',
    )

    @staticmethod
    def is_valid(link: str) -> bool:
        return YtDlp.YOUTUBE_REGX.match(link) is not None

    @staticmethod
    async def extract(
        link: str,
        video_parameters: VideoParameters,
    ) -> Tuple[str, str]:
        try:
            proc = await asyncio.create_subprocess_exec(
                'yt-dlp',
                '-g',
                '-f',
                f'best[width<=?{video_parameters.width}]'
                f'[height<=?{video_parameters.height}]',
                link,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            data = stdout.decode().split('\n')
            data[1] = data[0] if not data[1] else data[1]
            return data[0], data[1]
        except FileNotFoundError:
            raise YtDlpError('yt-dlp is not installed on your system')
