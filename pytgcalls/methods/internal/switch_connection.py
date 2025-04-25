import logging

from ntgcalls import ConnectionMode

from ...scaffold import Scaffold
from ...types.calls import CallSources

py_logger = logging.getLogger('pytgcalls')


class SwitchConnection(Scaffold):
    async def _switch_connection(self, chat_id: int):
        try:
            connection_mode = await self._binding.get_connection_mode(
                chat_id,
            )
            if connection_mode == ConnectionMode.STREAM and \
                    chat_id in self._pending_connections:
                connection = self._pending_connections[chat_id]
                await self._connect_call(
                    chat_id,
                    connection.media_description,
                    connection.config,
                    connection.payload,
                )
                if connection.presentation:
                    await self._join_presentation(
                        chat_id,
                        True,
                    )
                self._call_sources[chat_id] = CallSources()
                await self._update_sources(chat_id)
                self._pending_connections.pop(chat_id)
        except Exception as e:
            py_logger.debug(f'SetPresentationStatus: {e}')
