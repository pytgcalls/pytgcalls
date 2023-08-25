import logging

from typing import Union

from ..utilities.stream_params import StreamParams
from ...exceptions import NoMtProtoClientSet, NotInGroupCallError
from ...mtproto import BridgedClient
from ...scaffold import Scaffold
from ...to_async import ToAsync
from ...types.input_stream import InputStream

py_logger = logging.getLogger('pytgcalls')


class ChangeStream(Scaffold):
    async def change_stream(
        self,
        chat_id: Union[int, str],
        stream: InputStream,
    ):
        """Change the streaming file

        This method allow to change streaming file
        to a Group Call

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier of the target chat.
                Can be a direct id (int) or a username (str)
            stream (:obj:`~pytgcalls.types.InputStream()`):
                Input Streams descriptor, can be used also
                :obj:`~pytgcalls.types.AudioPiped()`,
                :obj:`~pytgcalls.types.AudioImagePiped()`,
                :obj:`~pytgcalls.types.AudioVideoPiped()` or
                :obj:`~pytgcalls.types.VideoPiped()`

        Raises:
            NoMtProtoClientSet: In case you try
                to call this method without any MtProto client
            NodeJSNotRunning: In case you try
                to call this method without do
                :meth:`~pytgcalls.PyTgCalls.start` before
            NoActiveGroupCall: In case you try
                to edit a not started group call
            FileNotFoundError: In case you try
                a non-existent file
            InvalidStreamMode: In case you try
                to set a void stream mode
            FFmpegNotInstalled: In case you try
                to use the Piped input stream, and
                you don't have ffmpeg installed
            NoAudioSourceFound: In case you try
                to play an audio file from a file
                without the sound
            NoVideoSourceFound: In case you try
                to play a video file from a file
                without the video
            InvalidVideoProportion: In case you try
                to play a video without correct
                proportions
            NotInGroupCallError: In case you try
                to leave a non-joined group call

        Example:
            .. code-block:: python
                :emphasize-lines: 10-15

                from pytgcalls import Client
                from pytgcalls import idle
                ...

                app = PyTgCalls(client)
                app.start()

                ...  # Call API methods

                app.change_stream(
                    -1001185324811,
                    AudioPiped(
                        'test.mp4',
                    )
                )

                idle()
        """
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
                    await StreamParams.get_stream_params(stream)
                )
            except FileNotFoundError:
                raise
            except Exception:
                raise NotInGroupCallError()
        else:
            raise NoMtProtoClientSet()
