from dataclasses import dataclass
from time import time
from typing import Any
from typing import Dict
from typing import Optional


@dataclass
class CacheEntry:
    time: int
    data: Any


class Cache:
    def __init__(self, expiry_time: int = 0):
        self._store: Dict[int, CacheEntry] = {}  # type: ignore
        self._expiry_time = expiry_time

    def get(self, chat_id: int):
        if chat_id in self._store:
            if self._store[chat_id].time == 0 or \
                    self._store[chat_id].time - int(time()) > 0:
                return self._store[chat_id].data
            else:
                self._store.pop(chat_id, None)
        return None

    def put(self, chat_id: int, data: Any, persistent: bool = False) -> None:
        self._store[chat_id] = CacheEntry(
            time=0
            if self._expiry_time == 0 or persistent else
            (int(time()) + self._expiry_time),
            data=data,
        )

    def update_cache(self, chat_id: int) -> None:
        if chat_id in self._store:
            self._store[chat_id].time = int(time()) + self._expiry_time

    @property
    def keys(self):
        now = int(time())
        return [
            chat_id
            for chat_id, entry in list(self._store.items())
            if entry.time == 0 or entry.time - now > 0
        ]

    def pop(self, chat_id: int) -> Optional[Any]:
        return self._store.pop(chat_id, None)
