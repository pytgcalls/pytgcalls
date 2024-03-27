from typing import List
from typing import Optional

from ntgcalls import RTCServer


class CallProtocol:
    def __init__(
        self,
        library_versions: List[str],
        p2p_allowed: Optional[bool] = None,
        rtc_servers: Optional[List[RTCServer]] = None,
    ):
        self.library_versions = library_versions
        self.p2p_allowed = p2p_allowed
        self.rtc_servers = rtc_servers
