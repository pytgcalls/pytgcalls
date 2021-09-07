import os

from .exceptions import NodeJSNotInstalled
from .exceptions import TooOldNodeJSVersion
from .exceptions import TooOldPyrogramVersion
from .exceptions import TooOldTelethonVersion
from .version_manager import VersionManager


class Environment:
    def __init__(
        self,
        min_js_version: str,
        min_pyrogram_version: str,
        min_telethon_version: str,
        client_name: str,
    ):
        self._REQUIRED_NODEJS_VERSION = min_js_version
        self._REQUIRED_PYROGRAM_VERSION = min_pyrogram_version
        self._REQUIRED_TELETHON_VERSION = min_telethon_version
        self._client_name = client_name

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
        if VersionManager.version_tuple(
            node_result,
        ) < VersionManager.version_tuple(
            self._REQUIRED_NODEJS_VERSION,
        ):
            raise TooOldNodeJSVersion(
                self._REQUIRED_NODEJS_VERSION,
                node_result,
            )
        if self._client_name == 'pyrogram':
            import pyrogram
            if VersionManager.version_tuple(
                pyrogram.__version__,
            ) < VersionManager.version_tuple(
                self._REQUIRED_PYROGRAM_VERSION,
            ):
                raise TooOldPyrogramVersion(
                    self._REQUIRED_PYROGRAM_VERSION,
                    pyrogram.__version__,
                )
        elif self._client_name == 'telethon':
            import telethon
            if VersionManager.version_tuple(
                telethon.__version__,
            ) < VersionManager.version_tuple(
                self._REQUIRED_TELETHON_VERSION,
            ):
                raise TooOldTelethonVersion(
                    self._REQUIRED_TELETHON_VERSION,
                    telethon.__version__,
                )
