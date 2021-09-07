import os
from stat import S_ISFIFO


class FileManager:
    @staticmethod
    def check_file_exist(
        path: str,
    ):
        if S_ISFIFO(os.stat(path).st_mode):
            return
        if not os.path.isfile(path):
            raise FileNotFoundError()
