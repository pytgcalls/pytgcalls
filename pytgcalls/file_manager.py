import logging
import os
from asyncio import TimeoutError
from stat import S_ISFIFO

from aiohttp import ClientConnectorError
from aiohttp import ClientResponse
from aiohttp import ClientSession

py_logger = logging.getLogger('pytgcalls')


class FileManager:
    @staticmethod
    async def check_file_exist(
        path: str,
    ):
        try:
            if 'http' in path:
                session = ClientSession()
                response: ClientResponse = await session.get(
                    path,
                    timeout=5,
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
