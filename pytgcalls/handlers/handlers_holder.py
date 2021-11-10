import asyncio
from typing import Callable
from typing import Dict
from typing import List


class HandlersHolder:
    def __init__(self):
        self._on_event_update: Dict[str, List[Callable]] = {
            'RAW_UPDATE_HANDLER': [],
            'STREAM_END_HANDLER': [],
            'INVITE_HANDLER': [],
            'KICK_HANDLER': [],
            'CLOSED_HANDLER': [],
            'LEFT_HANDLER': [],
            'PARTICIPANTS_LIST': [],
        }

    async def propagate(
        self,
        event_name: str,
        *args,
        **kwargs,
    ):
        for event in self._on_event_update[event_name]:
            asyncio.ensure_future(event(*args, **kwargs))

    def add_handler(
        self,
        event_name: str,
        func: Callable,
    ):
        self._on_event_update[event_name].append(func)
