class RemoveCall:
    def __init__(self, pytgcalls):
        self.pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    def _remove_call(self, chat_id: int):
        if chat_id in self.pytgcalls._calls:
            self.pytgcalls._calls.remove(chat_id)
