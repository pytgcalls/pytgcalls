from ...scaffold import Scaffold


class ClearCache(Scaffold):
    def _clear_cache(self, chat_id: int):
        """Clear all cache entries for a specific chat_id"""
        self._p2p_configs.pop(chat_id, None)
        self._cache_user_peer.pop(chat_id)
        self._need_unmute.discard(chat_id)
        self._presentations.discard(chat_id)
        self._call_sources.pop(chat_id, None)
        self._pending_connections.pop(chat_id, None)
        self._wait_connect.pop(chat_id, None)

    def _clear_all_caches(self):
        """Clear all caches to prevent memory leaks"""
        self._p2p_configs.clear()
        self._cache_user_peer.clear()
        self._need_unmute.clear()
        self._presentations.clear()
        self._call_sources.clear()
        self._pending_connections.clear()
        self._wait_connect.clear()
