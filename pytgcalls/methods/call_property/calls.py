class Calls:
    def __init__(self, pytgcalls):
        self._pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    @property
    def calls(self):
        return self._pytgcalls._calls
