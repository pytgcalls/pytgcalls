import asyncio
from typing import Dict

from .wait_counter_lock import WaitCounterLock


class ChatLock:
    def __init__(self):
        self._main_lock = asyncio.Lock()
        self._chat_lock: Dict[int, WaitCounterLock] = {}

    async def _remove_callback(self, chat_id: int):
        async with self._main_lock:
            if not self._chat_lock[chat_id].waiters():
                self._chat_lock.pop(chat_id, None)

    async def acquire(self, chat_id: int) -> WaitCounterLock:
        async with self._main_lock:
            self._chat_lock[chat_id] = self._chat_lock.get(
                chat_id,
            ) or WaitCounterLock(
                self._remove_callback,
                chat_id,
            )
            return self._chat_lock[chat_id]

    async def clear_all(self):
        """Clear all chat locks to prevent memory leaks"""
        async with self._main_lock:
            # Wait for all locks to be released
            for chat_id in list(self._chat_lock.keys()):
                lock = self._chat_lock[chat_id]
                while lock.waiters() > 0:
                    await asyncio.sleep(0.1)
            self._chat_lock.clear()

    def get_lock_count(self) -> int:
        """Get number of active chat locks"""
        return len(self._chat_lock)
