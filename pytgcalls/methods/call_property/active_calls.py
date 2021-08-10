class ActiveCalls:
    def __init__(self, pytgcalls):
        self._pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    @property
    def active_calls(self):
        return self._pytgcalls._active_calls
