import logging
from typing import Optional, Union

from ntgcalls import ConnectionNotFound, FileError

from ...exceptions import ClientNotStarted, NoMTProtoClientSet, NotInGroupCallError
from ...scaffold import Scaffold
from ...to_async import ToAsync
from ...types.raw.stream import Stream
from ..utilities.stream_params import StreamParams

py_logger = logging.getLogger('pytgcalls')

class ChangeStream(Scaffold):
    async def change_stream(
        self,
        chat_id: Union[int, str],
        stream: Optional[Stream] = None,
    ):
        if self._app is None:
            raise NoMTProtoClientSet()

        if not self._is_running:
            raise ClientNotStarted()

        chat_id = await self._resolve_chat_id(chat_id)
        try:
            await ToAsync(
                self._binding.change_stream,
                chat_id,
                await StreamParams.get_stream_params(stream),
            )
        except FileError as file_error:
            if "No such file or directory" in str(file_error):
                raise FileNotFoundError()
            raise file_error
        except ConnectionNotFound:
            raise NotInGroupCallError()
