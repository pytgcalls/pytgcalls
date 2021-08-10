class RemoveCall:
    def __init__(self, pytgcalls):
        self._pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    def _remove_call(self, chat_id: int):
        if chat_id in self._pytgcalls._calls:
            self._pytgcalls._calls.remove(chat_id)
