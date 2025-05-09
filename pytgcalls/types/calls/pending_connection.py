from ntgcalls import MediaDescription

from .group_call_config import GroupCallConfig


class PendingConnection:
    def __init__(
        self,
        media_description: MediaDescription,
        config: GroupCallConfig,
        payload: str,
        presentation: bool,
    ):
        self.media_description = media_description
        self.config = config
        self.payload = payload
        self.presentation = presentation
