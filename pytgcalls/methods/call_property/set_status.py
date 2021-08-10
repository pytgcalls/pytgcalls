class SetStatus:
    def __init__(self, pytgcalls):
        self._pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    def _set_status(self, chat_id: int, status: str):
        if chat_id in self._pytgcalls._active_calls:
            self._pytgcalls._active_calls[chat_id] = status
