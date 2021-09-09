import asyncio
import atexit
import signal
import subprocess
from asyncio.subprocess import Process
from typing import List, Optional


class WaitingBytes(Exception):
    def __init__(self):
        super().__init__(
            'Waiting bytes',
        )


class FFmpegAsync:
    DEFAULT_SEND_BUFFER = 65536
    DEFAULT_READ_BUFFER = 1024 * 1024

    def __init__(self):
        self._ffmpeg_async: Optional[Process] = None
        self._pipe_bytes: Optional[bytes] = None
        self._finished_read: bool = False
        self._is_paused: bool = False
        self._total_bytes: int = 0

        def cleanup():
            async def async_cleanup():
                if self._ffmpeg_async is not None:
                    try:
                        self._ffmpeg_async.send_signal(signal.SIGINT)
                        await asyncio.wait_for(
                            self._ffmpeg_async.communicate(),
                            timeout=3,
                        )
                    except ProcessLookupError:
                        pass
            asyncio.get_event_loop().run_until_complete(async_cleanup())
        atexit.register(cleanup)

    async def convert_audio_async(
        self,
        path: str,
        bitrate: int,
    ):
        asyncio.ensure_future(self._ffmpeg_runner([
            'ffmpeg',
            '-y',
            '-nostdin',
            '-i',
            path,
            '-f',
            's16le',
            '-ac',
            '1',
            '-ar',
            str(bitrate),
            'pipe:1',
        ]))

    async def convert_video_async(
        self,
        path: str,
        width: int,
        framerate: int,
    ):
        asyncio.ensure_future(self._ffmpeg_runner([
            'ffmpeg',
            '-y',
            '-nostdin',
            '-i',
            path,
            '-f',
            'rawvideo',
            '-r',
            str(framerate),
            '-vf',
            f'scale={width}:-1',
            'pipe:1',
        ]))

    async def _ffmpeg_runner(self, cmd: List):
        self._ffmpeg_async = await asyncio.create_subprocess_exec(
            *tuple(cmd),
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        try:
            while True:
                try:
                    if self._ffmpeg_async.stdout is None:
                        break
                    out = (await self._ffmpeg_async.stdout.read(self.DEFAULT_READ_BUFFER))
                    self._total_bytes += len(out)
                    if not out:
                        break
                    if self._pipe_bytes is None:
                        self._pipe_bytes = out
                    else:
                        self._pipe_bytes += out
                except TimeoutError:
                    pass
                while True:
                    if len(self._pipe_bytes) >= self.DEFAULT_READ_BUFFER * 10:
                        await asyncio.sleep(0.001)
                    else:
                        break
        except KeyboardInterrupt:
            pass
        self._finished_read = True

    async def pause(self):
        self._is_paused = True

    async def resume(self):
        self._is_paused = False

    @property
    def total_bytes(self):
        return self._total_bytes

    @property
    async def get_bytes(self):
        if self._pipe_bytes is not None:
            while True:
                await asyncio.sleep(0.001)
                bytes_len = len(self._pipe_bytes)
                if not self._is_paused:
                    if bytes_len >= self.DEFAULT_SEND_BUFFER or self._finished_read:
                        break
            buffer_size = self.DEFAULT_SEND_BUFFER \
                if bytes_len >= self.DEFAULT_SEND_BUFFER else bytes_len
            buffer = self._pipe_bytes[:buffer_size]
            self._pipe_bytes = self._pipe_bytes[buffer_size:]
            return buffer
        else:
            raise WaitingBytes()
