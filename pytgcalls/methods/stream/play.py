import logging
from pathlib import Path
from typing import Optional
from typing import Union

from ntgcalls import FileError
from ntgcalls import StreamMode

from ...exceptions import NoActiveGroupCall
from ...media_devices.input_device import InputDevice
from ...mtproto_required import mtproto_required
from ...mutex import mutex
from ...scaffold import Scaffold
from ...statictypes import statictypes
from ...types import CallConfig
from ...types import GroupCallConfig
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
            await self._connect_call(
                chat_id,  # type: ignore
                media_description,
                config,
                None,
            )
            if isinstance(config, GroupCallConfig):
                await self._join_presentation(
                    chat_id,
                    media_description.screen is not None,
                )
                await self._update_sources(chat_id)
        except FileError as e:
            raise FileNotFoundError(e)
        except Exception:
            if isinstance(config, GroupCallConfig):
                self._cache_user_peer.pop(chat_id)
            raise
