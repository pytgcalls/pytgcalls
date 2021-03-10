class AddCall:
    def __init__(self, pytgcalls):
        self.pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    def _add_call(self, chat_id: int):
        if chat_id not in self.pytgcalls._calls:
            self.pytgcalls._calls.append(chat_id)
