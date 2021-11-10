from dataclasses import dataclass
from time import time
from typing import Any
from typing import Dict
from typing import Optional


@dataclass
class CacheEntry:
    time: int
    expiry_time: int
    data: Any


class Cache:
    def __init__(self):
        self._store: Dict[int, CacheEntry] = {}

    def get(self, chat_id: int) -> Optional[Any]:
        if chat_id in self._store:
            if self._store[chat_id].time == 0 or \
                    self._store[chat_id].time - int(time()) > 0:
                return self._store[chat_id].data
            else:
                self._store.pop(chat_id, None)
        return None

    def put(self, chat_id: int, data: Any, expiry_time: int = 0) -> None:
        self._store[chat_id] = CacheEntry(
            time=0 if expiry_time == 0 else (int(time()) + expiry_time),
            expiry_time=expiry_time,
            data=data,
        )

    def keys(self):
        return [key for key in self._store]

    def pop(self, chat_id: int) -> Optional[Any]:
        return self._store.pop(chat_id, None)
