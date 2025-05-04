import asyncio
from typing import Optional
from typing import Union

from ntgcalls import ConnectionMode
from ntgcalls import ConnectionNotFound
from ntgcalls import MediaDescription
from ntgcalls import StreamMode
from ntgcalls import TelegramServerError

from ...exceptions import TimedOutAnswer
from ...scaffold import Scaffold
from ...types import CallConfig
from ...types import CallData
from ...types import GroupCallConfig
from ...types import PendingConnection
from ...types import RawCallUpdate


class ConnectCall(Scaffold):
    async def _connect_call(
        self,
        chat_id: int,
        media_description: MediaDescription,
        config: Union[CallConfig, GroupCallConfig],
        payload: Optional[str],
    ):
        for retries in range(4):
            try:
                self._wait_connect[chat_id] = self.loop.create_future()
                if isinstance(config, GroupCallConfig):
                    if not payload:
                        payload = await self._binding.create_call(
                            chat_id,
                        )
                    await self._binding.set_stream_sources(
                        chat_id,
                        StreamMode.CAPTURE,
                        media_description,
                    )
                    result_params = await self._app.join_group_call(
                        chat_id,
                        payload,
                        config.invite_hash,
                        media_description.camera is None and
                        media_description.screen is None,
                        self._cache_user_peer.get(chat_id),
                    )
                    await self._binding.connect(
                        chat_id,
                        result_params,
                        False,
                    )
                    connection_mode = await self._binding.get_connection_mode(
                        chat_id,
                    )
                    if connection_mode == ConnectionMode.STREAM and payload:
                        self._pending_connections[chat_id] = PendingConnection(
                            media_description,
                            config,
                            payload,
                            False,
                        )
                else:
                    data = self._p2p_configs.setdefault(
                        chat_id,
                        CallData(await self._app.get_dhc(), self.loop),
                    )
                    await self._binding.create_p2p_call(
                        chat_id,
                    )
                    await self._binding.set_stream_sources(
                        chat_id,
                        StreamMode.CAPTURE,
                        media_description,
                    )
                    data.g_a_or_b = await self._binding.init_exchange(
                        chat_id,
                        data.dh_config,
                        data.g_a_or_b,
                    )
                    if not data.outgoing:
                        await self._app.accept_call(
                            chat_id,
                            data.g_a_or_b,
                            self._binding.get_protocol(),
                        )
                    else:
                        await self._app.request_call(
                            chat_id,
                            data.g_a_or_b,
                            self._binding.get_protocol(),
                            media_description.camera is not None or
                            media_description.screen is not None,
                        )

                    try:
                        result: RawCallUpdate = await asyncio.wait_for(
                            data.wait_data,
                            timeout=config.timeout,
                        )
                        auth_params = await self._binding.exchange_keys(
                            chat_id,
                            result.g_a_or_b,
                            result.fingerprint,
                        )
                        if result.status & RawCallUpdate.Type.ACCEPTED:
                            result.protocol = await self._app.confirm_call(
                                chat_id,
                                auth_params.g_a_or_b,
                                auth_params.key_fingerprint,
                                self._binding.get_protocol(),
                            )
                        await self._binding.connect_p2p(
                            chat_id,
                            result.protocol.rtc_servers,
                            result.protocol.library_versions,
                            result.protocol.p2p_allowed,
                        )
                    except asyncio.TimeoutError:
                        try:
                            await self._binding.stop(chat_id)
                        except ConnectionNotFound:
                            pass
                        await self._app.discard_call(chat_id, True)
                        raise TimedOutAnswer()
                    finally:
                        self._p2p_configs.pop(chat_id, None)
                await self._wait_connect[chat_id]
                break
            except TelegramServerError:
                if retries == 3 or chat_id > 0:
                    raise
                self._log_retries(retries)
            except Exception:
                try:
                    await self._binding.stop(chat_id)
                except ConnectionNotFound:
                    pass
                raise
            finally:
                self._wait_connect.pop(chat_id, None)
