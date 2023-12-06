from .exceptions import TooOldHydrogramVersion
from .exceptions import TooOldPyrogramVersion
from .exceptions import TooOldTelethonVersion
from .version_manager import VersionManager


class Environment:
    def __init__(
        self,
        min_pyrogram_version: str,
        min_telethon_version: str,
        min_hydrogram_version: str,
        client_name: str,
    ):
        self._REQUIRED_PYROGRAM_VERSION = min_pyrogram_version
        self._REQUIRED_TELETHON_VERSION = min_telethon_version
        self._REQUIRED_HYDROGRAM_VERSION = min_hydrogram_version
        self._client_name = client_name

    def check_environment(self):
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
        elif self._client_name == 'hydrogram':
            import hydrogram
            if VersionManager.version_tuple(
                    hydrogram.__version__,
            ) < VersionManager.version_tuple(
                self._REQUIRED_HYDROGRAM_VERSION,
            ):
                raise TooOldHydrogramVersion(
                    self._REQUIRED_HYDROGRAM_VERSION,
                    hydrogram.__version__,
                )
