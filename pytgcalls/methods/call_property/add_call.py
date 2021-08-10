class AddCall:
    def __init__(self, pytgcalls):
        self._pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    def _add_call(self, chat_id: int):
        if chat_id not in self._pytgcalls._calls:
            self._pytgcalls._calls.append(chat_id)
