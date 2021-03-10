class Calls:
    def __init__(self, pytgcalls):
        self.pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    @property
    def calls(self):
        return self.pytgcalls._calls
