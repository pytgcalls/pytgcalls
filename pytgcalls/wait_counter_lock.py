import asyncio


class WaitCounterLock:
    def __init__(self):
        self._lock = asyncio.Lock()
        self._waiters = 0

    def waiters(self):
        return self._waiters

    async def __aenter__(self):
        self._waiters += 1
        await self._lock.acquire()
        self._waiters -= 1
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self._lock.locked():
            self._lock.release()
