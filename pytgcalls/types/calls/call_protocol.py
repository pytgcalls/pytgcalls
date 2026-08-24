from ntgcalls import RTCServer


class CallProtocol:
    def __init__(
        self,
        library_versions: list[str],
        p2p_allowed: bool | None = None,
        rtc_servers: list[RTCServer] | None = None,
        conference_supported: bool | None = None,
        custom_parameters: str | None = None,
    ):
        self.library_versions = library_versions
        self.p2p_allowed = p2p_allowed
        self.rtc_servers = rtc_servers
        self.conference_supported = conference_supported
        self.custom_parameters = custom_parameters
