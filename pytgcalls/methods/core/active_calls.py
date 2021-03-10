class ActiveCalls:
    def __init__(self, pytgcalls):
        self.pytgcalls = pytgcalls

    def _chat_id_as_int(func):
        def __chat_id_as_int(self, chat_id, *args, **kwargs):
            return func(self, int(chat_id), *args, **kwargs)
        return __chat_id_as_int

    @property
    def calls(self):
        return self._calls

    @property
    def num_calls(self):
        return len(self.calls)

    @_chat_id_as_int
    def _add_call(self, chat_id: int):
        if chat_id not in self.calls:
            self._calls.append(chat_id)

    @_chat_id_as_int
    def _rm_call(self, chat_id: int):
        if chat_id in self.calls:
            self._calls.remove(chat_id)

    @property
    def active_calls(self):
        return self._active_calls

    @property
    def num_active_calls(self):
        return len(self.active_calls)

    @_chat_id_as_int
    def _is_playing(self, chat_id: int):
        return chat_id in self.active_calls

    @_chat_id_as_int
    def _add_active_call(self, chat_id: int):
        if not self._is_playing(chat_id):
            self._active_calls[chat_id] = "playing"

    @_chat_id_as_int
    def _rm_active_call(self, chat_id: int):
        if self._is_playing(chat_id):
            del self._active_calls[chat_id]

    @_chat_id_as_int
    def _set_status(self, chat_id: int, status: str):
        if self._is_playing(chat_id):
            self._active_calls[chat_id] = status
