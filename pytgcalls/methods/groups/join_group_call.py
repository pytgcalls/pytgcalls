import logging
from typing import Optional, Union

from ntgcalls import ConnectionError, FileError, InvalidParams
from ...exceptions import AlreadyJoinedError, ClientNotStarted, NoActiveGroupCall, NoMTProtoClientSet, TelegramServerError, UnMuteNeeded
from ...mtproto import BridgedClient
from ...scaffold import Scaffold
from ...to_async import ToAsync
from ...types import JoinedVoiceChat
from ...types.input_stream.stream import Stream
from ..utilities.stream_params import StreamParams

py_logger = logging.getLogger('pytgcalls')


class JoinGroupCall(Scaffold):
    async def join_group_call(
        self,
        chat_id: Union[int, str],
        stream: Optional[Stream] = None,
        invite_hash: str = None,
        join_as=None,
    ):
        """
        Join a group call.

        :param chat_id: Chat ID of the group call.
        :param stream: Optional stream to be used in the call.
        :param invite_hash: Invite hash for the group call.
        :param join_as: User to join as.
        :raises FileNotFoundError: If the specified file is not found.
        :raises AlreadyJoinedError: If the user is already joined.
        :raises UnMuteNeeded: If unmute is needed.
        :raises TelegramServerError: If there's an error on the Telegram server.
        :raises NoActiveGroupCall: If there is no active group call.
        :raises ClientNotStarted: If the client is not started.
        :raises NoMTProtoClientSet: If no MTProto client is set.
        """
        if join_as is None:
            join_as = self._cache_local_peer

        chat_id = await self._resolve_chat_id(chat_id)
        self._cache_user_peer.put(chat_id, join_as)

        if self._app is not None:
            if self._is_running:
                try:
                    chat_call = await self._app.get_full_chat(chat_id)
                    if chat_call is None:
                        raise NoActiveGroupCall()

                    media_description = await StreamParams.get_stream_params(stream)
                    call_params = await ToAsync(self._binding.create_call, chat_id, media_description)

                    result_params = await self._app.join_group_call(
                        chat_id,
                        call_params,
                        invite_hash,
                        media_description.video is None,
                        self._cache_user_peer.get(chat_id),
                    )

                    await ToAsync(self._binding.connect, chat_id, result_params)

                    participants = await self._app.get_group_call_participants(chat_id)
                    self._handle_participants(participants, chat_id)

                    await self._on_event_update.propagate(
                        'RAW_UPDATE_HANDLER',
                        self,
                        JoinedVoiceChat(chat_id),
                    )

                except FileError:
                    raise FileNotFoundError()
                except ConnectionError:
                    raise AlreadyJoinedError()
                except InvalidParams:
                    raise UnMuteNeeded()
                except Exception as e:
                    py_logger.error(f"Error joining group call: {e}")
                    raise TelegramServerError()

            else:
                raise ClientNotStarted()
        else:
            raise NoMTProtoClientSet()

    async def _handle_participants(self, participants, chat_id):
        """
        Handle group call participants.

        :param participants: List of participants.
        :param chat_id: Chat ID of the group call.
        """
        for participant in participants:
            if participant.user_id == BridgedClient.chat_id(self._cache_local_peer):
                self._need_unmute[chat_id] = participant.muted_by_admin
