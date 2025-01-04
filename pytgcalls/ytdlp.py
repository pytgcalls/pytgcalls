import asyncio
import logging
import re
import shlex
from typing import Optional, Tuple

from .exceptions import YtDlpError
from .ffmpeg import cleanup_commands
from .types.raw import VideoParameters

py_logger = logging.getLogger('pytgcalls')

class YtDlp:
    YOUTUBE_REGX = re.compile(
        r'^((?:https?:)?//)?((?:www|m)\.)?'
        r'(youtube(-nocookie)?\.com|youtu.be)'
        r'(/(?:[\w\-]+\?v=|embed/|live/|v/)?)'
        r'([\w\-]+)(\S+)?$',
    )

    @staticmethod
    def is_valid(link: str) -> bool:
        """Check if the link matches the YouTube URL pattern."""
        return bool(YtDlp.YOUTUBE_REGX.match(link))

    @staticmethod
    async def extract(
        link: Optional[str],
        video_parameters: VideoParameters,
        add_commands: Optional[str] = None,
    ) -> Tuple[Optional[str], Optional[str]]:
        """Extract video URLs using yt-dlp."""
        if link is None:
            return None, None

        commands = [
            'yt-dlp',
            '-g',
            '-f',
            'bestvideo[vcodec~="(vp09|avc1)"]+m4a/best',
            '-S',
            f'res:{min(video_parameters.width, video_parameters.height)}',
            '--no-warnings',
        ]

        if add_commands:
            commands += await cleanup_commands(
                shlex.split(add_commands),
                'yt-dlp',
                ['-f', '-g', '--no-warnings'],
            )

        commands.append(link)

        py_logger.debug(f'Running with command: {" ".join(commands)}')

        try:
            proc = await asyncio.create_subprocess_exec(
                *commands,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await YtDlp._execute_with_timeout(proc)
            return YtDlp._parse_video_urls(stdout, stderr)
        except FileNotFoundError:
            raise YtDlpError('yt-dlp is not installed on your system')
        except asyncio.TimeoutError:
            raise YtDlpError('yt-dlp process timeout')

    @staticmethod
    async def _execute_with_timeout(proc: asyncio.subprocess.Process) -> Tuple[str, str]:
        """Helper to execute the subprocess and handle timeouts."""
        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=20,
            )
            return stdout, stderr
        finally:
            proc.terminate()

    @staticmethod
    def _parse_video_urls(stdout: bytes, stderr: bytes) -> Tuple[Optional[str], Optional[str]]:
        """Parse the video URLs from yt-dlp output."""
        if stderr:
            raise YtDlpError(stderr.decode())

        data = stdout.decode().strip().split('\n')
        if data:
            return data[0], data[1] if len(data) >= 2 else data[0]
        raise YtDlpError('No video URLs found')
