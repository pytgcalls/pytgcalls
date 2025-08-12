from ...scaffold import Scaffold


class ClearCache(Scaffold):
    def _clear_cache(self, chat_id: int):
        # Drop MTProto caches to avoid stale state after leaving calls
        try:
            # Not awaited: synchronous cache drop
            self._app.drop_cache(chat_id)  # type: ignore[attr-defined]
            self._app.drop_phone_call(chat_id)  # type: ignore[attr-defined]
        except Exception:
            pass
        self._p2p_configs.pop(chat_id, None)
        self._cache_user_peer.pop(chat_id)
        self._need_unmute.discard(chat_id)
        self._presentations.discard(chat_id)
        self._call_sources.pop(chat_id, None)
        self._pending_connections.pop(chat_id, None)
