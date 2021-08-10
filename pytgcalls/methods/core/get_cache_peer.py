class GetCachePeer:
    def __init__(self, pytgcalls):
        self._pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    def get_cache_peer(self):
        return self._pytgcalls._cache_local_peer
