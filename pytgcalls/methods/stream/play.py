import asyncio
import logging
from pathlib import Path
from typing import Optional
from typing import Union

from ntgcalls import ConnectionNotFound
from ntgcalls import FileError
from ntgcalls import StreamMode
from ntgcalls import TelegramServerError
from ntgcalls import TransportParseException

from ...exceptions import NoActiveGroupCall
from ...exceptions import TimedOutAnswer
from ...exceptions import UnMuteNeeded
from ...media_devices.input_device import InputDevice
from ...mtproto_required import mtproto_required
from ...mutex import mutex
from ...scaffold import Scaffold
from ...statictypes import statictypes
from ...types import CallConfig
from ...types import CallData
from ...types import GroupCallConfig
from ...types import RawCallUpdate
from ...types.raw import Stream
from ..utilities.stream_params import StreamParams

py_logger = logging.getLogger('pytgcalls')


class Play(Scaffold):
    @statictypes
    @mtproto_required
    @mutex
    async def play(
        self,
        chat_id: Union[int, str],
        stream: Optional[Union[str, Path, InputDevice, Stream]] = None,
        config: Optional[Union[CallConfig, GroupCallConfig]] = None,
    ):
        chat_id = await self.resolve_chat_id(chat_id)
        is_p2p = chat_id > 0  # type: ignore
        if config is None:
            config = GroupCallConfig() if not is_p2p else CallConfig()
        if not is_p2p and not isinstance(config, GroupCallConfig):
            raise ValueError(
                'Group call config must be provided for group calls',
            )
        media_description = await StreamParams.get_stream_params(
            stream,
        )

        if chat_id in await self._binding.calls():
            try:
                return await self._binding.set_stream_sources(
                    chat_id,
                    StreamMode.CAPTURE,
                    media_description,
                )
            except FileError as e:
                raise FileNotFoundError(e)

        if isinstance(config, GroupCallConfig):
            self._cache_user_peer.put(
                chat_id,
                self._cache_local_peer
                if config.join_as is None else config.join_as,
            )

            chat_call = await self._app.get_full_chat(
                chat_id,
            )
            if chat_call is None:
                if config.auto_start:
                    await self._app.create_group_call(
                        chat_id,
                    )
                else:
                    raise NoActiveGroupCall()

        try:
            for retries in range(4):
                try:
                    self._wait_connect[chat_id] = self.loop.create_future()
                    if isinstance(config, GroupCallConfig):
                        payload: str = await self._binding.create_call(
                            chat_id,
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
                    else:
                        data = self._p2p_configs.setdefault(
                            chat_id,
                            CallData(await self._app.get_dhc(), self.loop),
                        )
                        await self._binding.create_p2p_call(
                            chat_id,
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
                    if retries == 3 or is_p2p:
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

            if isinstance(config, GroupCallConfig):
                await self._join_presentation(
                    chat_id,
                    media_description.screen is not None,
                )
                await self._update_sources(chat_id)
        except FileError as e:
            raise FileNotFoundError(e)
        except TransportParseException:
            raise UnMuteNeeded()
        except Exception:
            if isinstance(config, GroupCallConfig):
                self._cache_user_peer.pop(chat_id)
            raise
