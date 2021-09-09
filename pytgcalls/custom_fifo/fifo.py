import asyncio
import sys

from .ffmpeg_async import FFmpegAsync, WaitingBytes


class Fifo:
    def __init__(self):
        self.is_running = False

    async def mkfifo(
        self,
        ffmpeg: FFmpegAsync
    ):
        self.is_running = True
        while True:
            try:
                read_bytes = await ffmpeg.get_bytes
                sys.stdout.buffer.write(read_bytes)
                sys.stdout.buffer.flush()
                if len(read_bytes) == 0:
                    break
            except WaitingBytes:
                await asyncio.sleep(0.001)
            except BrokenPipeError:
                break
        self.is_running = True
