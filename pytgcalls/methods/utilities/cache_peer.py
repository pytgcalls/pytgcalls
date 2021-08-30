from pytgcalls.scaffold import Scaffold


class CachePeer(Scaffold):
    @property
    def cache_peer(self):
        return self._cache_local_peer
