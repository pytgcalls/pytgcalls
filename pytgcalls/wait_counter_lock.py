import asyncio
from typing import Optional
from typing import Type


class WaitCounterLock:
    def __init__(self) -> None:
        # Initialize the asyncio Lock and a counter for the number of waiters
        self._lock: asyncio.Lock = asyncio.Lock()
        self._waiters: int = 0

    def waiters(self) -> int:
        # Return the current number of waiters waiting to acquire the lock
        return self._waiters

    async def __aenter__(self) -> 'WaitCounterLock':
        # Increment waiter count before attempting to acquire the lock
        self._waiters += 1
        await self._lock.acquire()
        # Decrement waiter count after acquiring the lock
        self._waiters -= 1
        # Return self to allow usage as async context manager
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[object],
    ) -> None:
        # Release the lock when exiting the async context, if it is currently held
        if self._lock.locked():
            self._lock.release()
