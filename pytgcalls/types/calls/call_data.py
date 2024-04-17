import asyncio
from asyncio import Future
from typing import Any
from typing import Optional

from ntgcalls import DhConfig


class CallData:
    def __init__(
        self,
        dhc_config: Any,
        loop: asyncio.AbstractEventLoop,
        g_a_hash: Optional[bytes] = None,
    ):
        self.dh_config = DhConfig(
            dhc_config.g, dhc_config.p, dhc_config.random,
        )
        self.g_a_or_b: Optional[bytes] = g_a_hash
        self.outgoing: bool = g_a_hash is None
        self.wait_data: Future = loop.create_future()
