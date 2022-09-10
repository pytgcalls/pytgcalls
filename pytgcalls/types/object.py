from .groups import AlreadyJoined
from .groups import ErrorDuringJoin
from .groups import JoinedVoiceChat
from .groups import LeftVoiceChat
from .groups import MutedCall
from .groups import NotInGroupCall
from .groups import UpgradeNeeded
from .stream import ChangedStream
from .stream import MutedStream
from .stream import PausedStream
from .stream import ResumedStream
from .stream import StreamDeleted
from .stream import StreamTime
from .stream import UnMutedStream


class Object:
    @staticmethod
    def from_dict(
        data: dict,
    ):
        event_name = data['result']
        chat_id = int(data['chat_id'])
        if event_name == 'PAUSED_STREAM':
            return PausedStream(chat_id)
        elif event_name == 'RESUMED_STREAM':
            return ResumedStream(chat_id)
        elif event_name == 'CHANGED_STREAM':
            return ChangedStream(chat_id)
        elif event_name == 'JOINED_VOICE_CHAT':
            return JoinedVoiceChat(chat_id)
        elif event_name == 'NOT_IN_GROUP_CALL':
            return NotInGroupCall(chat_id)
        elif event_name == 'JOIN_ERROR':
            return ErrorDuringJoin(chat_id)
        elif event_name == 'ALREADY_JOINED':
            return AlreadyJoined(chat_id)
        elif event_name == 'LEFT_VOICE_CHAT':
            return LeftVoiceChat(chat_id)
        elif event_name == 'STREAM_DELETED':
            return StreamDeleted(chat_id)
        elif event_name == 'MUTED_STREAM':
            return MutedStream(chat_id)
        elif event_name == 'UNMUTED_STREAM':
            return UnMutedStream(chat_id)
        elif event_name == 'APP_UPGRADE_NEEDED':
            return UpgradeNeeded(chat_id)
        elif event_name == 'PLAYED_TIME':
            return StreamTime(data['time'])
        elif event_name == 'UNMUTE_NEEDED':
            return MutedCall(chat_id)
