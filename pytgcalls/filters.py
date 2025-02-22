import inspect
from typing import Callable
from typing import List
from typing import Optional
from typing import Union

from .mtproto import BridgedClient
from .pytgcalls import PyTgCalls
from .types import ChatUpdate
from .types import Device
from .types import Direction
from .types import GroupCallParticipant
from .types import StreamEnded
from .types import StreamFrames
from .types import Update
from .types import UpdatedGroupCallParticipant


class Filter:
    async def __call__(self, client: PyTgCalls, update: Update):
        raise NotImplementedError

    def __invert__(self):
        return InvertFilter(self)

    def __and__(self, other):
        return AndFilter(self, other)

    def __or__(self, other):
        return OrFilter(self, other)


class InvertFilter(Filter):
    def __init__(self, base):
        self.base = base

    async def __call__(self, client: PyTgCalls, update: Update):
        if inspect.iscoroutinefunction(self.base.__call__):
            x = await self.base(client, update)
        else:
            x = await client.loop.run_in_executor(
                client.executor,
                self.base,
                client, update,
            )

        return not x


class AndFilter(Filter):
    def __init__(self, base, other):
        self.base = base
        self.other = other

    async def __call__(self, client: PyTgCalls, update: Update):
        if inspect.iscoroutinefunction(self.base.__call__):
            x = await self.base(client, update)
        else:
            x = await client.loop.run_in_executor(
                client.executor,
                self.base,
                client,
                update,
            )

        # short circuit
        if not x:
            return False

        if inspect.iscoroutinefunction(self.other.__call__):
            y = await self.other(client, update)
        else:
            y = await client.loop.run_in_executor(
                client.executor,
                self.other,
                client,
                update,
            )

        return x and y


class OrFilter(Filter):
    def __init__(self, base, other):
        self.base = base
        self.other = other

    async def __call__(self, client: PyTgCalls, update: Update):
        if inspect.iscoroutinefunction(self.base.__call__):
            x = await self.base(client, update)
        else:
            x = await client.loop.run_in_executor(
                client.executor,
                self.base,
                client,
                update,
            )

        # short circuit
        if x:
            return True

        if inspect.iscoroutinefunction(self.other.__call__):
            y = await self.other(client, update)
        else:
            y = await client.loop.run_in_executor(
                client.executor,
                self.other,
                client,
                update,
            )

        return x or y


CUSTOM_FILTER_NAME = 'CustomFilter'


def create(func: Callable, name: Optional[str] = None, **kwargs) -> Filter:
    return type(
        name or func.__name__ or CUSTOM_FILTER_NAME,
        (Filter,),
        {'__call__': func, **kwargs},
    )()


async def _me_filter(_, client: PyTgCalls, u: Update):
    if isinstance(u, UpdatedGroupCallParticipant):
        chat_peer = client.cache_user_peer.get(u.chat_id)
        if chat_peer:
            return BridgedClient.chat_id(
                chat_peer,
            ) == u.participant.user_id if chat_peer else False
    return False


me = create(_me_filter)


class stream_end(Filter):
    def __init__(
        self,
        stream_type: Optional[StreamEnded.Type] = None,
        device: Optional[Device] = None,
    ):
        self.stream_type = stream_type
        self.device = device

    async def __call__(self, client: PyTgCalls, update: Update):
        if isinstance(update, StreamEnded):
            return (
                (
                    self.stream_type is None or
                    self.stream_type & update.stream_type
                ) and (
                    self.device is None or
                    self.device & update.device
                )
            )


# noinspection PyPep8Naming
class chat(Filter, set):
    def __init__(
        self,
        chats: Optional[Union[int, str, List[Union[int, str]]]] = None,
    ):
        chats = [] if chats is None else chats \
            if isinstance(chats, list) else [chats]
        super().__init__(chats)

    async def __call__(self, client: PyTgCalls, update: Update):
        return any([
            await client.resolve_chat_id(c) == update.chat_id
            for c in self
        ])


# noinspection PyPep8Naming
class chat_update(Filter):
    def __init__(self, flags: ChatUpdate.Status):
        self.flags = flags

    async def __call__(self, client: PyTgCalls, update: Update):
        if isinstance(update, ChatUpdate):
            return self.flags & update.status
        return False


class call_participant(Filter):
    def __init__(self, flags: Optional[GroupCallParticipant.Action] = None):
        self.flags = flags

    async def __call__(self, client: PyTgCalls, update: Update):
        if isinstance(update, UpdatedGroupCallParticipant):
            if self.flags is None:
                return True
            return self.flags & update.participant.action
        return False


class stream_frame(Filter):
    def __init__(
        self,
        directions: Optional[Direction] = None,
        devices: Optional[Device] = None,
    ):
        self.directions = directions
        self.devices = devices

    async def __call__(self, client: PyTgCalls, update: Update):
        if isinstance(update, StreamFrames):
            return (
                (
                    self.directions is None or
                    self.directions & update.direction
                ) and (
                    self.devices is None or
                    self.devices & update.device
                )
            )
        return False
