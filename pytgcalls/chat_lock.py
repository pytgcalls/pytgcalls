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
