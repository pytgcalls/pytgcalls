import logging

from ...scaffold import Scaffold

py_logger = logging.getLogger('pytgcalls')


class LogRetries(Scaffold):
    @staticmethod
    def _log_retries(r: int):
        (py_logger.warning if r >= 1 else py_logger.info)(
            f'Telegram is having some internal server issues. '
            f'Retrying {r + 1} of 3',
        )
