import asyncio
import logging

from ...exceptions import PyTgCallsAlreadyRunning
from ...pytgcalls_session import PyTgCallsSession
from ...scaffold import Scaffold

py_logger = logging.getLogger('pytgcalls')


class Start(Scaffold):
    async def start(self):
        if not self._is_running:
            self._is_running = True
            self._env_checker.check_environment()
            self._app.add_handler(self._handle_mtproto_updates)
            if not self._app.is_connected:
                await self._app.start()

            self._my_id = await self._app.get_id()
            self._cache_local_peer = await self._app.resolve_peer(
                self._my_id,
            )
            if self._app.no_updates:
                py_logger.warning(
                    f'Using {self._app.package_name.capitalize()} '
                    'client in no_updates mode is not recommended. '
                    'This mode may cause unexpected behavior or '
                    'limitations.',
                )
            else:
                self._handle_mtproto()

            self._binding.on_stream_end(
                lambda chat_id, stream_type, device:
                asyncio.run_coroutine_threadsafe(
                    self._handle_stream_ended(chat_id, stream_type, device),
                    self.loop,
                ),
            )
            self._binding.on_upgrade(
                lambda chat_id, state:
                asyncio.run_coroutine_threadsafe(
                    self._update_status(chat_id, state),
                    self.loop,
                ),
            )
            self._binding.on_connection_change(
                lambda chat_id, net_state: asyncio.run_coroutine_threadsafe(
                    self._handle_connection_changed(chat_id, net_state),
                    self.loop,
                ),
            )
            self._binding.on_signaling(
                lambda chat_id, data: asyncio.run_coroutine_threadsafe(
                    self._emit_sig_data(chat_id, data),
                    self.loop,
                ),
            )
            self._binding.on_frames(
                lambda chat_id, mode, device, frames:
                asyncio.run_coroutine_threadsafe(
                    self._handle_stream_frame(
                        chat_id,
                        mode,
                        device,
                        frames,
                    ),
                    self.loop,
                ),
            )
            self._binding.on_request_broadcast_part(
                lambda chat_id, part_request:
                asyncio.run_coroutine_threadsafe(
                    self._request_broadcast_part(
                        chat_id,
                        part_request,
                    ),
                    self.loop,
                ),
            )
            self._binding.on_request_broadcast_timestamp(
                lambda chat_id:
                asyncio.run_coroutine_threadsafe(
                    self._request_broadcast_timestamp(chat_id),
                    self.loop,
                ),
            )
            await PyTgCallsSession().start()
        else:
            raise PyTgCallsAlreadyRunning()
