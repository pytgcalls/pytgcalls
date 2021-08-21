from pyrogram import raw

from pytgcalls.scaffold import Scaffold


class CachePeer(Scaffold):
    @property
    def cache_peer(self) -> raw.base.InputUser:
        return self._cache_local_peer
