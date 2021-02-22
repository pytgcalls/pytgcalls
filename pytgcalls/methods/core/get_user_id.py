class GetUserId:
    def __init__(self, pytgcalls):
        self.pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    def get_cache_id(self):
        return self.pytgcalls._my_id
