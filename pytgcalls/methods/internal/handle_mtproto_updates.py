from ntgcalls import ConnectionError
from ntgcalls import ConnectionNotFound

from ...exceptions import CallBusy
from ...exceptions import CallDeclined
from ...exceptions import CallDiscarded
from ...mtproto import BridgedClient
from ...scaffold import Scaffold
from ...types import CallData
from ...types import ChatUpdate
from ...types import GroupCallParticipant
from ...types import RawCallUpdate
from ...types import Update
from ...types import UpdatedGroupCallParticipant


class HandleMTProtoUpdates(Scaffold):
    async def _handle_mtproto_updates(self, update: Update):
        chat_id = update.chat_id
        if update.chat_id in self._p2p_configs:
            p2p_config = self._p2p_configs[chat_id]
            if not p2p_config.wait_data.done():
                if isinstance(update, RawCallUpdate):
                    if update.status & RawCallUpdate.Type.UPDATED_CALL:
                        p2p_config.wait_data.set_result(
                            update,
                        )
                if isinstance(update, ChatUpdate) and \
                        p2p_config.outgoing:
                    if update.status & ChatUpdate.Status.DISCARDED_CALL:
                        self._wait_connect.pop(chat_id, None)
                        p2p_config.wait_data.set_exception(
                            CallBusy(
                                chat_id,
                            ) if update.status &
                            ChatUpdate.Status.BUSY_CALL else
                            CallDeclined(
                                chat_id,
                            ),
                        )
        if chat_id in self._wait_connect and \
                not self._wait_connect[chat_id].done():
            if isinstance(update, ChatUpdate):
                if update.status & ChatUpdate.Status.DISCARDED_CALL:
                    self._wait_connect[chat_id].set_exception(
                        CallDiscarded(
                            chat_id,
                        ),
                    )
        if isinstance(update, RawCallUpdate):
            if update.status & RawCallUpdate.Type.REQUESTED:
                self._p2p_configs[chat_id] = CallData(
                    await self._app.get_dhc(),
                    self.loop,
                    update.g_a_or_b,
                )
                update = ChatUpdate(
                    chat_id,
                    ChatUpdate.Status.INCOMING_CALL,
                )
        if isinstance(update, RawCallUpdate):
            if update.status & RawCallUpdate.Type.SIGNALING_DATA:
                try:
                    await self._binding.send_signaling(
                        update.chat_id,
                        update.signaling_data,
                    )
                except (ConnectionNotFound, ConnectionError):
                    pass
        if isinstance(update, ChatUpdate):
            if update.status & ChatUpdate.Status.LEFT_CALL:
                await self._clear_call(chat_id)
        if isinstance(update, UpdatedGroupCallParticipant):
            participant = update.participant
            action = participant.action
            chat_peer = self._cache_user_peer.get(chat_id)
            user_id = participant.user_id
            if chat_id in self._call_sources:
                call_sources = self._call_sources[chat_id]
                was_camera = user_id in call_sources.camera
                was_screen = user_id in call_sources.presentation

                if was_camera != participant.video_camera:
                    if participant.video_info:
                        self._call_sources[chat_id].camera[
                            user_id
                        ] = participant.video_info.endpoint
                        try:
                            await self._binding.add_incoming_video(
                                chat_id,
                                participant.video_info.endpoint,
                                participant.video_info.sources,
                            )
                        except (ConnectionNotFound, ConnectionError):
                            pass
                    elif user_id in self._call_sources[chat_id].camera:
                        try:
                            await self._binding.remove_incoming_video(
                                chat_id,
                                self._call_sources[
                                    chat_id
                                ].camera[user_id],
                            )
                        except (ConnectionNotFound, ConnectionError):
                            pass
                        self._call_sources[chat_id].camera.pop(
                            user_id, None,
                        )

                if was_screen != participant.screen_sharing:
                    if participant.presentation_info:
                        self._call_sources[chat_id].presentation[
                            user_id
                        ] = participant.presentation_info.endpoint
                        try:
                            await self._binding.add_incoming_video(
                                chat_id,
                                participant.presentation_info.endpoint,
                                participant.presentation_info.sources,
                            )
                        except (ConnectionNotFound, ConnectionError):
                            pass
                    elif user_id in self._call_sources[
                        chat_id
                    ].presentation:
                        try:
                            await self._binding.remove_incoming_video(
                                chat_id,
                                self._call_sources[
                                    chat_id
                                ].presentation[user_id],
                            )
                        except (ConnectionNotFound, ConnectionError):
                            pass
                        self._call_sources[chat_id].presentation.pop(
                            user_id, None,
                        )

            if chat_peer:
                is_self = BridgedClient.chat_id(
                    chat_peer,
                ) == participant.user_id if chat_peer else False
                if is_self:
                    if action == GroupCallParticipant.Action.LEFT:
                        if await self._clear_call(chat_id):
                            await self._propagate(
                                ChatUpdate(
                                    chat_id,
                                    ChatUpdate.Status.KICKED,
                                ),
                                self,
                            )
                    if (
                            chat_id in self._need_unmute and
                            action == GroupCallParticipant.Action.UPDATED and
                            not participant.muted_by_admin
                    ):
                        await self._update_status(
                            chat_id,
                            await self._binding.get_state(chat_id),
                        )
                        await self._switch_connection(chat_id)

                    if (
                            participant.muted_by_admin and
                            action != GroupCallParticipant.Action.LEFT
                    ):
                        self._need_unmute.add(chat_id)
                    else:
                        self._need_unmute.discard(chat_id)
        if not isinstance(update, RawCallUpdate):
            await self._propagate(
                update,
                self,
            )
