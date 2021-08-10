class AddActiveCall:
    def __init__(self, pytgcalls):
        self._pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    def _add_active_call(self, chat_id: int):
        if chat_id not in self._pytgcalls._active_calls:
            self._pytgcalls._active_calls[chat_id] = 'playing'
