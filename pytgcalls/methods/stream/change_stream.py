import logging
from typing import Union

from ntgcalls import FileError

from ...exceptions import NoMtProtoClientSet
from ...exceptions import NotInGroupCallError
from ...mtproto import BridgedClient
from ...scaffold import Scaffold
from ...to_async import ToAsync
from ...types import ChangedStream
from ...types.input_stream import InputStream
from ..utilities.stream_params import StreamParams

py_logger = logging.getLogger('pytgcalls')


class ChangeStream(Scaffold):
    async def change_stream(
        self,
        chat_id: Union[int, str],
        stream: InputStream,
    ):
        try:
            chat_id = int(chat_id)
        except ValueError:
            chat_id = BridgedClient.chat_id(
                await self._app.resolve_peer(chat_id),
            )

        if self._app is not None:
            try:
                await ToAsync(
                    self._binding.changeStream,
                    chat_id,
                    await StreamParams.get_stream_params(stream),
                )
            except FileError:
                raise FileNotFoundError()
            except Exception:
                raise NotInGroupCallError()

            await self._on_event_update.propagate(
                'RAW_UPDATE_HANDLER',
                self,
                ChangedStream(chat_id),
            )
        else:
            raise NoMtProtoClientSet()
