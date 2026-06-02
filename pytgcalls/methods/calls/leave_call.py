import asyncio
import logging
import os
from typing import Union

from ntgcalls import ConnectionNotFound

from ...exceptions import NoActiveGroupCall
from ...exceptions import NotInCallError
from ...mtproto_required import mtproto_required
from ...mutex import mutex
from ...scaffold import Scaffold
from ...statictypes import statictypes

py_logger = logging.getLogger('pytgcalls')

# Maximum seconds to wait for ntgcalls to process stop().
# If exceeded the C++ thread is presumed deadlocked and we log an error,
# reap zombie children, and proceed so the Python side can continue.
_STOP_TIMEOUT: float = 10.0


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


class LeaveCall(Scaffold):
    @statictypes
    @mtproto_required
    @mutex
    async def leave_call(
        self,
        chat_id: Union[int, str],
        close: bool = False,
    ):
        chat_id = await self.resolve_chat_id(chat_id)
        is_p2p_waiting = (
            chat_id in self._p2p_configs and
            not self._p2p_configs[chat_id].wait_data.done()
        )
        if not is_p2p_waiting:

            try:
                await asyncio.wait_for(
                    self._binding.stop(chat_id),
                    timeout=_STOP_TIMEOUT,
                )
            except ConnectionNotFound:
                raise NotInCallError()
            except asyncio.TimeoutError:
                zombies = _reap_zombie_children()
                py_logger.error(
                    'binding.stop() timed out after %.1fs for chat %d '
                    '(reaped %d zombie child(ren)); proceeding with MTProto '
                    'leave anyway',
                    _STOP_TIMEOUT,
                    chat_id,
                    zombies,
                )
                # Do NOT re-raise: we still want to send the MTProto
                # leave_group_call so Telegram removes us from the call.

        if chat_id < 0:  # type: ignore
            chat_call = await self._app.get_full_chat(
                chat_id,
            )

            if chat_call is None:
                raise NoActiveGroupCall()

            await self._app.leave_group_call(
                chat_id,
            )
        else:
            await self._app.discard_call(chat_id, False)
        if is_p2p_waiting:
            self._p2p_configs.pop(chat_id)
            return
        if chat_id < 0:  # type: ignore
            self._clear_cache(chat_id)  # type: ignore

        if chat_id < 0 and close:  # type: ignore
            await self._app.close_voice_chat(chat_id)
