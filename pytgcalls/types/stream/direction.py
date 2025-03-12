from enum import auto

from ntgcalls import StreamMode

from ..flag import Flag


class Direction(Flag):
    OUTGOING = auto()
    INCOMING = auto()

    @staticmethod
    def from_raw(direction: StreamMode):
        if direction == StreamMode.CAPTURE:
            return Direction.OUTGOING
        if direction == StreamMode.PLAYBACK:
            return Direction.INCOMING
        return None

    def to_raw(self):
        if self is Direction.OUTGOING:
            return StreamMode.CAPTURE
        if self is Direction.INCOMING:
            return StreamMode.PLAYBACK
        return None
