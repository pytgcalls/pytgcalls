import asyncio

from ...pytgcalls_session import PyTgCallsSession
from ...scaffold import Scaffold


class BindingRunner(Scaffold):
    async def _start_binding(self):
        @self._binding.on_update()
        async def update_handler(data: dict):
            if 'action' in data:
                if data['action'] == 'join_voice_call_request':
                    return await self._join_voice_call(data['payload'])
                elif data['action'] == 'leave_call_request':
                    return await self._leave_voice_call(data)
                elif data['action'] == 'stream_audio_ended':
                    return await self._stream_ended_handler(data, True)
                elif data['action'] == 'stream_video_ended':
                    return await self._stream_ended_handler(data, False)
                elif data['action'] == 'upgrade_video_status':
                    return await self._set_video_call_status(data)
                elif data['action'] == 'update_request':
                    return await self._raw_update_handler(data)
            return {
                'result': 'INVALID_REQUEST',
            }

        @self._binding.on_connect()
        async def connect():
            try:
                self._wait_until_run.set_result(None)
            except Exception as e:
                print(e)

            pass

        await PyTgCallsSession().start()
        loop = asyncio.get_event_loop()
        started_core = loop.create_future()
        self._async_core = asyncio.ensure_future(
            self._binding.connect(
                started_core,
                self._my_id,
            ),
        )
        try:
            await started_core
        except KeyboardInterrupt:
            pass
