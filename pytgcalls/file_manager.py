import os
from stat import S_ISFIFO

import httpx
from httpx import Response


class FileManager:
    @staticmethod
    async def check_file_exist(
        path: str,
    ):
        if 'http' in path:
            async with httpx.AsyncClient() as client:
                response: Response = await client.head(path)
                if response.status_code == 200:
                    return
        if S_ISFIFO(os.stat(path).st_mode):
            return
        if not os.path.isfile(path):
            raise FileNotFoundError()
