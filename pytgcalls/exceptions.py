class TooOldPyrogramVersion(Exception):
    def __init__(
            self,
            version_needed: str,
            pyrogram_version: str,
    ):
        super().__init__(
            f'Needed pyrogram {version_needed}+, '
            'actually installed is '
            f'{pyrogram_version}',
        )


class TooOldTelethonVersion(Exception):
    def __init__(
            self,
            version_needed: str,
            telethon_version: str,
    ):
        super().__init__(
            f'Needed telethon {version_needed}+, '
            'actually installed is '
            f'{telethon_version}',
        )


class TooOldHydrogramVersion(Exception):
    def __init__(
            self,
            version_needed: str,
            hydrogram_version: str,
    ):
        super().__init__(
            f'Needed hydrogram {version_needed}+, '
            'actually installed is '
            f'{hydrogram_version}',
        )


class NoMTProtoClientSet(Exception):
    def __init__(self):
        super().__init__(
            'No MTProto client set',
        )


class NoActiveGroupCall(Exception):
    def __init__(self):
        super().__init__(
            'No active group call',
        )


class TimedOutAnswer(Exception):
    def __init__(self):
        super().__init__(
            'Timed out waiting for an answer',
        )


class CallDeclined(Exception):
    def __init__(self, user_id: int):
        super().__init__(
            f'Call declined by {user_id}',
        )


class CallBusy(Exception):
    def __init__(self, user_id: int):
        super().__init__(
            f'The user {user_id} is busy',
        )


class CallDiscarded(Exception):
    def __init__(self, user_id: int):
        super().__init__(
            f'Call discarded by {user_id}',
        )


class NotInCallError(Exception):
    def __init__(self):
        super().__init__(
            'The userbot is not in a call',
        )


class ClientNotStarted(Exception):
    def __init__(self):
        super().__init__(
            'Ensure you have started the process with start() '
            'before calling this method',
        )


class PyTgCallsAlreadyRunning(Exception):
    def __init__(self):
        super().__init__(
            'PyTgCalls client is already running',
        )


class TooManyCustomApiDecorators(Exception):
    def __init__(self):
        super().__init__(
            'Too Many Custom Api Decorators',
        )


class InvalidMTProtoClient(Exception):
    def __init__(self):
        super().__init__(
            'Invalid MTProto Client',
        )


class NoVideoSourceFound(Exception):
    def __init__(self, path: str):
        super().__init__(
            f'No video source found on "{path}"',
        )


class InvalidVideoProportion(Exception):
    def __init__(self, message: str):
        super().__init__(
            message,
        )


class NoAudioSourceFound(Exception):
    def __init__(self, path: str):
        super().__init__(
            f'No audio source found on "{path}"',
        )


class ImageSourceFound(Exception):
    def __init__(self, path: str):
        super().__init__(
            f'Found an image source on "{path}"',
        )


class LiveStreamFound(Exception):
    def __init__(self, path: str):
        super().__init__(
            f'Found a livestream on "{path}"',
        )


class YtDlpError(Exception):
    def __init__(self, message: str):
        super().__init__(
            message,
        )


class UnMuteNeeded(Exception):
    def __init__(self):
        super().__init__(
            'Needed to unmute the userbot',
        )


class MTProtoClientNotConnected(Exception):
    def __init__(self):
        super().__init__(
            'MTProto client not connected',
        )


class UnsupportedMethod(Exception):
    def __init__(self):
        super().__init__(
            'Unsupported method for this kind of call',
        )
