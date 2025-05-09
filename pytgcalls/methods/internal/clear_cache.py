from ...scaffold import Scaffold


class ClearCache(Scaffold):
    def _clear_cache(self, chat_id: int):
        self._p2p_configs.pop(chat_id, None)
        self._cache_user_peer.pop(chat_id)
        self._need_unmute.discard(chat_id)
