class ActiveCalls:
    def __init__(self, pytgcalls):
        self.pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    @property
    def active_calls(self):
        return self.pytgcalls._active_calls
