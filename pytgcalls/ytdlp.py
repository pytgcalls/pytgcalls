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
        return bool(YtDlp.YOUTUBE_REGX.match(link))

    @staticmethod
    async def extract(
        link: str,
        video_parameters: VideoParameters,
    ) -> Tuple[str, str]:
        try:
            process = await asyncio.create_subprocess_exec(
                'yt-dlp',
                '-g',
                '-f',
                f'best[width<=?{video_parameters.width}][height<=?{video_parameters.height}]',
                link,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()
            if stderr:
                raise YtDlpError(stderr.decode())
            data = stdout.decode().strip().split('\n')
            if len(data) >= 2:
                return data[0], data[1]
            elif data:
                return data[0], ''
            else:
                raise YtDlpError('No video URLs found')
        except FileNotFoundError:
            raise YtDlpError('yt-dlp is not installed on your system')
