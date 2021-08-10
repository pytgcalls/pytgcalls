class GetCacheId:
    def __init__(self, pytgcalls):
        self._pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    def get_cache_id(self):
        return self._pytgcalls._my_id
