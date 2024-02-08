import asyncio
import re
import shlex
from typing import Optional
from typing import Tuple

from .exceptions import YtDlpError
from .ffmpeg import cleanup_commands
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
        link: Optional[str],
        video_parameters: VideoParameters,
        add_commands: Optional[str],
    ) -> Tuple[Optional[str], Optional[str]]:
        if link is None:
            return None, None

        commands = [
            'yt-dlp',
            '-g',
            '-f',
            f'best[width<=?{video_parameters.width}]'
            f'[height<=?{video_parameters.height}]',
        ]

        if add_commands:
            commands += await cleanup_commands(
                shlex.split(add_commands),
                'yt-dlp',
            )

        commands.append(link)

        try:
            proc = await asyncio.create_subprocess_exec(
                *commands,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            if stderr:
                raise YtDlpError(stderr.decode())
            data = stdout.decode().strip().split('\n')
            if len(data) >= 2:
                return data[0], data[1]
            elif data:
                return data[0], None
            else:
                raise YtDlpError('No video URLs found')
        except FileNotFoundError:
            raise YtDlpError('yt-dlp is not installed on your system')
