import os

import pyrogram

from .exceptions import NodeJSNotInstalled
from .exceptions import TooOldNodeJSVersion
from .exceptions import TooOldPyrogramVersion
from .version_manager import VersionManager


class Environment:
    def __init__(
        self,
        min_js_version: str,
        min_pyrogram_version: str,
    ):
        self._REQUIRED_NODEJS_VERSION = min_js_version
        self._REQUIRED_PYROGRAM_VERSION = min_pyrogram_version

    def check_environment(self):
        def get_version(package_check):
            result_cmd = os.popen(f'{package_check} -v').read()
            result_cmd = result_cmd.replace('v', '')
            if len(result_cmd) == 0:
                return None
            return result_cmd

        node_result = get_version('node')
        if node_result is None:
            raise NodeJSNotInstalled(
                self._REQUIRED_NODEJS_VERSION,
            )
        if VersionManager.version_tuple(node_result) < \
                VersionManager.version_tuple(self._REQUIRED_NODEJS_VERSION):
            raise TooOldNodeJSVersion(
                self._REQUIRED_NODEJS_VERSION,
                node_result,
            )
        if VersionManager.version_tuple(pyrogram.__version__) < \
                VersionManager.version_tuple(self._REQUIRED_PYROGRAM_VERSION):
            raise TooOldPyrogramVersion(
                self._REQUIRED_PYROGRAM_VERSION,
                pyrogram.__version__,
            )
