import asyncio
from asyncio import Future
from typing import Any
from typing import Dict


class UpdateSolver:
    def __init__(self):
        self._list_pending_update: Dict[str, Future] = {}

    async def wait_future_update(
        self,
        update_id: str,
    ) -> Any:
        loop = asyncio.get_event_loop()
        self._list_pending_update[update_id] = loop.create_future()
        return await self._list_pending_update[update_id]

    def resolve_future_update(
        self,
        update_id: str,
        update: Any,
    ) -> bool:
        if update_id in self._list_pending_update:
            self._list_pending_update[update_id].set_result(update)
            del self._list_pending_update[update_id]
            return True
        return False
