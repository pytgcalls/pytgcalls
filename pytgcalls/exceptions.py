class NodeJSNotInstalled(Exception):
    def __init__(
            self,
            version_needed: str,
    ):
        super().__init__(
            f'Please install node ({version_needed}+)'
        )


class TooOldNodeJSVersion(Exception):
    def __init__(
            self,
            version_needed: str,
            node_version: str
    ):
        super().__init__(
            f'Needed node {version_needed}+, '
            'actually installed is '
            f'{node_version}',
        )


class TooOldPyrogramVersion(Exception):
    def __init__(
            self,
            version_needed: str,
            pyrogram_version: str
    ):
        super().__init__(
            f'Needed pyrogram {version_needed}+, '
            'actually installed is '
            f'{pyrogram_version}',
        )


class InvalidStreamMode(Exception):
    def __init__(self):
        super().__init__()


class PyrogramNotSet(Exception):
    def __init__(self):
        super().__init__()


class NodeJSNotRunning(Exception):
    def __init__(self):
        super().__init__()


class NoActiveVoiceChat(Exception):
    def __init__(self):
        super().__init__()


class WaitPreviousPingRequest(Exception):
    def __init__(self):
        super().__init__()


class PyTgCallsAlreadyRunning(Exception):
    def __init__(self):
        super().__init__()


class TooManyCustomApiDecorators(Exception):
    def __init__(self):
        super().__init__()
