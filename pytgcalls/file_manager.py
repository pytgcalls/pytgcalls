import logging
import os
from asyncio import TimeoutError
from stat import S_ISFIFO
from typing import Dict
from typing import Optional

from aiohttp import ClientConnectorError
from aiohttp import ClientResponse
from aiohttp import ClientSession

from .types.input_stream.video_tools import check_support

py_logger = logging.getLogger('pytgcalls')


class FileManager:
    @staticmethod
    async def check_file_exist(
        path: str,
        headers: Optional[Dict[str, str]] = None,
    ):
        try:
            if check_support(path):
                session = ClientSession()
                response: ClientResponse = await session.get(
                    path,
                    timeout=5,
                    headers=headers,
                )
                response.close()
                await session.close()
                if response.status == 200 or \
                        response.status == 403:
                    return
                else:
                    py_logger.info(
                        f'{path} returned with {response.status} code',
                    )
        except ClientConnectorError:
            pass
        except TimeoutError:
            pass
        if S_ISFIFO(os.stat(path).st_mode):
            return
        if not os.path.isfile(path):
            raise FileNotFoundError()
