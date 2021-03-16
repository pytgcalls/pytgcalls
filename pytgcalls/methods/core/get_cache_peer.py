class GetCachePeer:
    def __init__(self, pytgcalls):
        self.pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    def get_cache_peer(self):
        return self.pytgcalls._cache_local_peer
