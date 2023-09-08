from ...scaffold import Scaffold
from ...types.groups import JoinedVoiceChat
from ...types.groups import LeftVoiceChat
from ...types.object import Object
from ...types.stream import ChangedStream
from ...types.stream import PausedStream
from ...types.stream import ResumedStream
from ...types.stream import StreamDeleted


class RawUpdateHandler(Scaffold):
    async def _raw_update_handler(
        self,
        data: dict,
    ):
        pass
        #await self._on_event_update.propagate(
        #    'RAW_UPDATE_HANDLER',
        #    self,
        #    obj,
        #)
