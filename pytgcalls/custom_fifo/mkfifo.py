import asyncio
import json
import sys
from json import JSONDecodeError

from pytgcalls.custom_fifo.ffmpeg_async import FFmpegAsync
from pytgcalls.custom_fifo.fifo import Fifo


async def main():
    ffmpeg = FFmpegAsync()
    if sys.argv[2] == 'video':
        await ffmpeg.convert_video_async(
            sys.argv[1],
            int(sys.argv[3]),
            int(sys.argv[4]),
        )
    else:
        await ffmpeg.convert_audio_async(
            sys.argv[1],
            int(sys.argv[3]),
        )
    fifo = Fifo()

    async def commands_handler():
        loop = asyncio.get_event_loop()
        while fifo.is_running:
            result = await loop.run_in_executor(None, sys.stdin.buffer.readline)
            try:
                data = json.loads(result)
                if data['request'] == 'PAUSE':
                    await ffmpeg.pause()
                elif data['request'] == 'RESUME':
                    await ffmpeg.resume()
                elif data['request'] == 'GET_FILE_SIZE':
                    sys.stderr.buffer.write(
                        json.dumps({
                            'result': data['request'],
                            'data': ffmpeg.total_bytes,
                            'uid': data['uid'],
                        }).encode(),
                    )
                    sys.stderr.buffer.flush()
            except JSONDecodeError:
                pass

    asyncio.ensure_future(commands_handler())
    await fifo.mkfifo(ffmpeg)
    sys.stderr.buffer.write(
        json.dumps({
            'result': 'ENDED',
            'file_size': ffmpeg.total_bytes,
        }).encode(),
    )
    sys.stderr.buffer.flush()

asyncio.get_event_loop().run_until_complete(main())
