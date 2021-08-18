import re

import requests

from .__version__ import __version__
from .version_manager import VersionManager


class PyTgCallsSession:
    notice_displayed = False

    def __init__(self):
        if not self.notice_displayed:
            PyTgCallsSession.notice_displayed = True
            print(
                f'PyTgCalls v{__version__}, Copyright (C) '
                f'2021 Laky-64 <https://github.com/Laky-64>\n'
                'Licensed under the terms of the GNU Lesser '
                'General Public License v3 or later (LGPLv3+)\n',
            )
            remote_stable_ver = self._remote_version('master')
            remote_dev_ver = self._remote_version('dev')
            if VersionManager.version_tuple(__version__) > \
                    VersionManager.version_tuple(remote_stable_ver + '.99'):
                remote_ver = remote_readable_ver = remote_dev_ver
                my_ver = __version__
            else:
                remote_readable_ver = remote_stable_ver
                remote_ver = remote_stable_ver + '.99'
                my_ver = __version__ + '.99'

            if VersionManager.version_tuple(remote_ver) > \
                    VersionManager.version_tuple(my_ver):
                print(
                    '\033[93m'
                    f'Update Available!\n'
                    f'New PyTgCalls v{remote_readable_ver} is now available!\n'
                    '\033[0m',
                )

    @staticmethod
    def _remote_version(branch: str):
        return re.findall(
            '__version__ = \'(.*?)\'', requests.get(
                f'https://raw.githubusercontent.com/'
                f'pytgcalls/pytgcalls/{branch}'
                f'/pytgcalls/__version__.py',
            ).text,
        )[0]
