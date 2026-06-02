import asyncio
import logging
import os
from pathlib import Path
from typing import Optional
from typing import Union

from ntgcalls import FileError
from ntgcalls import StreamMode

from ...exceptions import NoActiveGroupCall
from ...exceptions import NtgCallsStreamSwitchTimeout
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

# Maximum seconds to wait for ntgcalls to swap stream sources.
# If this deadline is exceeded the C++ thread is presumed deadlocked
# and we raise NtgCallsStreamSwitchTimeout so the caller can decide
# whether to leave + re-join rather than waiting forever.
_SET_STREAM_SOURCES_TIMEOUT: float = 15.0


def _reap_zombie_children() -> int:
    """
    Non-blocking reap of any zombie child processes left behind by
    ntgcalls / ffmpeg when the C++ engine kills subprocesses but never
    calls waitpid().  Returns the number of children reaped.
    """
    reaped = 0
    while True:
        try:
            pid, _ = os.waitpid(-1, os.WNOHANG)
            if pid <= 0:
                break
            reaped += 1
            py_logger.debug('reaped zombie child pid=%d', pid)
        except ChildProcessError:
            break
    return reaped


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
        is_presentation = media_description.screen is not None

        if chat_id in await self._binding.calls():
            try:
                try:
                    await asyncio.wait_for(
                        self._binding.set_stream_sources(
                            chat_id,
                            StreamMode.CAPTURE,
                            media_description,
                        ),
                        timeout=_SET_STREAM_SOURCES_TIMEOUT,
                    )
                except asyncio.TimeoutError:
                    zombies = _reap_zombie_children()
                    py_logger.error(
                        'set_stream_sources timed out after %.1fs for chat %d '
                        '(reaped %d zombie child(ren)); raising '
                        'NtgCallsStreamSwitchTimeout',
                        _SET_STREAM_SOURCES_TIMEOUT,
                        chat_id,
                        zombies,
                    )
                    raise NtgCallsStreamSwitchTimeout(chat_id)

                if isinstance(config, GroupCallConfig):
                    await self._join_presentation(
                        chat_id,
                        is_presentation,
                    )
                return
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
                    is_presentation,
                )
                await self._update_sources(chat_id)
        except FileError as e:
            raise FileNotFoundError(e)
        except Exception:
            if isinstance(config, GroupCallConfig):
                self._cache_user_peer.pop(chat_id)
            raise
