from ...scaffold import Scaffold
from ...types.call_holder import CallHolder
from ...types.stream import StreamAudioEnded
from ...types.stream import StreamVideoEnded


class StreamEndedHandler(Scaffold):
    async def _stream_ended_handler(
        self,
        params: dict,
        is_audio: bool,
    ):
        chat_id = int(params['chat_id'])
        self._call_holder.set_status(
            chat_id,
            CallHolder.IDLE,
        )
        await self._on_event_update.propagate(
            'STREAM_END_HANDLER',
            self,
            StreamAudioEnded(
                chat_id,
            ) if is_audio else StreamVideoEnded(chat_id),
        )
        return {
            'result': 'OK',
        }
