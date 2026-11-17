import asyncio
import logging
from bisect import insort
from enum import IntEnum
from operator import itemgetter
from time import time
from typing import Any

from ..types import GroupCallMessage
from ..types import GroupCallParticipant
from ..types import UpdatedGroupCallMessage
from ..types import UpdatedGroupCallParticipant
from .bridged_client import BridgedClient

py_logger = logging.getLogger('pytgcalls')


class GroupCall:
    REQUEST_PER_PAGE = 50
    WAIT_FOR_UPDATES_TIMEOUT = 3
    RELOAD_STALE_TIMEOUT = 16

    class ApplySliceSource(IntEnum):
        FULL_RELOADED = 0
        SLICE_LOADED = 1
        UNKNOWN_LOADED = 2
        UPDATE_RECEIVED = 3

    class QueuedType(IntEnum):
        VERSIONED_PARTICIPANT = 0
        PARTICIPANT = 1
        CALL = 2

    def __init__(
        self,
        app: BridgedClient,
        chat_id: int,
        input_call: Any,
    ):
        self._app = app
        self.chat_id = chat_id
        self.input = input_call
        self.schedule_date: int | None = None
        self.discarded = False
        self.in_call = False
        self.join_ssrc: int | None = None
        self.conference = False
        self.messages_enabled = False
        self.messages_min_price = 0
        self._version = 0
        self._participants: dict[int, GroupCallParticipant] = {}
        self._participant_peer_by_audio_ssrc: dict[int, int] = {}
        self._apply_volume_from_min: set[int] = set()
        self._next_offset = ''
        self._server_participants_count = 0
        self._all_participants_loaded = False
        self._saved_full: Any | None = None
        self._reloaded_from: dict[int, GroupCallParticipant] | None = None
        self._queued_updates: list[tuple[tuple[int, int], Any]] = []
        self._applying_queued_updates = False
        self._reload_by_queued_updates_timer: asyncio.Task | None = None
        self._reload_request: asyncio.Future | None = None
        self._reload_last_finished: float | None = None
        self._participants_request: asyncio.Future | None = None
        self._unknown_spoken_ssrcs: set[int] = set()
        self._unknown_participant_peers_request: asyncio.Future | None = None
        self._participant_updates: list[UpdatedGroupCallParticipant] = []
        self._participant_updates_task: asyncio.Task | None = None
        self._sending_message_ids: set[int] = set()
        self._message_ids: set[int] = set()
        self._skipped_message_ids: set[int] = set()
        self._conference_id_auto_increment = 0
        self._conference_id_by_random_id: dict[int, int] = {}

    @staticmethod
    def call_id(input_call) -> int | str:
        return getattr(input_call, 'slug', None) or input_call.id

    @property
    def id(self) -> int | str:
        return self.call_id(self.input)

    @property
    def loaded(self) -> bool:
        return self._version > 0

    @property
    def participants(self) -> list[GroupCallParticipant]:
        return list(self._participants.values())

    def destroy(self):
        self.in_call = False
        if self._reload_by_queued_updates_timer is not None:
            self._reload_by_queued_updates_timer.cancel()
            self._reload_by_queued_updates_timer = None
        self._queued_updates.clear()
        self._unknown_spoken_ssrcs.clear()
        self._sending_message_ids.clear()
        self._message_ids.clear()
        self._skipped_message_ids.clear()
        self._conference_id_by_random_id.clear()

    def fire_participant_update(self, update: UpdatedGroupCallParticipant):
        self._participant_updates.append(update)
        if self._participant_updates_task is None:
            self._participant_updates_task = asyncio.create_task(
                self.propagate_participant_updates(),
            )

    async def propagate_participant_updates(self):
        while self._participant_updates:
            try:
                await self._app._propagate(self._participant_updates.pop(0))
            except Exception as e:
                py_logger.debug(
                    'Group Call Participants: Handler failed: %s',
                    e,
                )
        self._participant_updates_task = None

    async def enqueue_update(self, update):
        initial = not self._version
        if update.__class__.__name__ == 'UpdateGroupCall':
            version = update.call.version
            if not self._applying_queued_updates and (
                not self._version or self._version == version
            ):
                py_logger.debug(
                    'Group Call Participants: Apply updateGroupCall %d -> %d',
                    self._version,
                    version,
                )
                await self.apply_enqueued_update(update)
            elif not self._version or self._version <= version:
                py_logger.debug(
                    'Group Call Participants: Queue updateGroupCall %d -> %d',
                    self._version,
                    version,
                )
                insort(
                    self._queued_updates,
                    ((version, self.QueuedType.CALL), update),
                    key=itemgetter(0),
                )
        else:
            version = update.version
            increment = any(
                participant.versioned for participant in update.participants
            )
            required = version - 1 if increment else version
            if not self._applying_queued_updates and self._version == required:
                py_logger.debug(
                    'Group Call Participants: '
                    'Apply updateGroupCallParticipant %d (%s)',
                    self._version,
                    increment,
                )
                await self.apply_enqueued_update(update)
            elif self._version <= required:
                py_logger.debug(
                    'Group Call Participants: '
                    'Queue updateGroupCallParticipant %d -> %d (%s)',
                    self._version,
                    version,
                    increment,
                )
                insort(
                    self._queued_updates,
                    (
                        (
                            version,
                            self.QueuedType.VERSIONED_PARTICIPANT
                            if increment
                            else self.QueuedType.PARTICIPANT,
                        ),
                        update,
                    ),
                    key=itemgetter(0),
                )
        await self.process_queued_updates(initial)
        if not self._version:
            await self.reload()

    async def apply_enqueued_update(self, update):
        self._applying_queued_updates = True
        try:
            if update.__class__.__name__ == 'UpdateGroupCall':
                self.apply_call_fields(update.call)
            else:
                py_logger.debug(
                    'Group Call Participants: '
                    'Set from updateGroupCallParticipants %d -> %d',
                    self._version,
                    update.version,
                )
                self._version = update.version or 1
                for p_update in self.apply_participants_slice(
                    update.participants,
                    self.ApplySliceSource.UPDATE_RECEIVED,
                ):
                    self.fire_participant_update(p_update)
        finally:
            self._applying_queued_updates = False

    async def process_queued_updates(self, initial: bool = False):
        if not self._version or self._applying_queued_updates:
            return

        size = len(self._queued_updates)
        while self._queued_updates:
            (version, queued_type), update = self._queued_updates[0]
            incremented = queued_type == self.QueuedType.VERSIONED_PARTICIPANT
            if version < self._version or (
                version == self._version and incremented and not initial
            ):
                self._queued_updates.pop(0)
            elif version == self._version or (
                version == self._version + 1 and incremented
            ):
                self._queued_updates.pop(0)
                await self.apply_enqueued_update(update)
            else:
                break
        if not self._queued_updates:
            if self._reload_by_queued_updates_timer is not None:
                self._reload_by_queued_updates_timer.cancel()
                self._reload_by_queued_updates_timer = None
        elif (
            len(self._queued_updates) != size
            or self._reload_by_queued_updates_timer is None
        ):
            if self._reload_by_queued_updates_timer is not None:
                self._reload_by_queued_updates_timer.cancel()
            self._reload_by_queued_updates_timer = asyncio.create_task(
                self.reload_by_queued_updates(),
            )

    async def reload_by_queued_updates(self):
        await asyncio.sleep(self.WAIT_FOR_UPDATES_TIMEOUT)
        self._reload_by_queued_updates_timer = None
        await self.reload()

    async def reload_if_stale(self):
        if (
            not self._server_participants_count
            and not self._all_participants_loaded
        ):
            await self.reload()
        elif (
            self._reload_last_finished is None
            or asyncio.get_running_loop().time()
            > self._reload_last_finished + self.RELOAD_STALE_TIMEOUT
        ):
            await self.reload()

    async def reload(self):
        if self._applying_queued_updates:
            return
        if self._reload_request is not None:
            await self._reload_request
            return
        request = asyncio.get_running_loop().create_future()
        self._reload_request = request
        if self._participants_request is not None:
            self._participants_request.set_result(None)
            self._participants_request = None

        py_logger.debug(
            'Group Call Participants: Reloading with queued: %d',
            len(self._queued_updates),
        )

        try:
            while self._queued_updates:
                await self.apply_enqueued_update(
                    self._queued_updates.pop(0)[1],
                )
            if self._reload_by_queued_updates_timer is not None:
                self._reload_by_queued_updates_timer.cancel()
                self._reload_by_queued_updates_timer = None

            result = await self._app.get_group_call(self.input, 3)
            if self.request_participants_after_reload(result):
                self._saved_full = result
                await self.request_participants()
            else:
                self.process_full_call_fields(result)
                await self.finish_participants_slice_request()
        except Exception as e:
            py_logger.debug('Group Call Participants: Reload failed: %s', e)
        finally:
            self._saved_full = None
            self._reload_request = None
            self._reload_last_finished = asyncio.get_running_loop().time()
            request.set_result(None)
        if self.in_call:
            await self.load_participants()

    async def load_participants(self):
        while self.loaded and not self._all_participants_loaded:
            await self.request_participants()

    async def request_participants(self):
        if self._saved_full is None:
            if self._participants_request is not None:
                await self._participants_request
                return
            elif self._reload_request is not None:
                await self._reload_request
                return
            elif self._all_participants_loaded:
                return
        request = asyncio.get_running_loop().create_future()
        self._participants_request = request
        try:
            result = await self._app.get_group_participants(
                self.input,
                [],
                self._next_offset
                if self._saved_full is None
                else self._saved_full.participants_next_offset,
                self.REQUEST_PER_PAGE,
            )
        except Exception as e:
            py_logger.debug('Group Call Participants: Slice failed: %s', e)
            if self._participants_request is not request:
                return
            self._participants_request = None
            self.process_saved_full_call()
            self._server_participants_count = len(self._participants)
            self._all_participants_loaded = True
        else:
            if self._participants_request is not request:
                return
            self._participants_request = None
            reloaded = self.process_saved_full_call()
            self._next_offset = result.next_offset
            self.apply_participants_slice(
                result.participants,
                self.ApplySliceSource.FULL_RELOADED
                if reloaded
                else self.ApplySliceSource.SLICE_LOADED,
            )
            self._server_participants_count = result.count
            if not result.participants:
                self._all_participants_loaded = True
        request.set_result(None)
        await self.finish_participants_slice_request()

    def request_participants_after_reload(self, call) -> bool:
        received = len(call.participants)
        size = getattr(call.call, 'participants_count', 0)
        return received < size and received < len(self._participants)

    def process_saved_full_call(self) -> bool:
        if self._saved_full is None:
            return False
        saved_full, self._saved_full = self._saved_full, None
        self.process_full_call_fields(saved_full)
        return True

    def process_full_call_fields(self, call):
        if not hasattr(call.call, 'version'):
            self.discarded = True
            return
        if self._reloaded_from is None and self._all_participants_loaded:
            self._reloaded_from = self._participants
        self._participants = {}
        self._participant_peer_by_audio_ssrc.clear()
        self._apply_volume_from_min.clear()
        self._all_participants_loaded = False

        self.apply_participants_slice(
            call.participants,
            self.ApplySliceSource.FULL_RELOADED,
        )
        self._next_offset = call.participants_next_offset

        self.apply_call_fields(call.call)

    async def finish_participants_slice_request(self):
        await self.process_queued_updates()
        if self._all_participants_loaded and self._reloaded_from is not None:
            was, self._reloaded_from = self._reloaded_from, None
            now = dict(self._participants)
            for user_id, participant in was.items():
                if user_id not in now and participant.source != self.join_ssrc:
                    self.fire_participant_update(
                        UpdatedGroupCallParticipant(
                            self.chat_id,
                            GroupCallParticipant.Action.LEFT,
                            participant,
                        ),
                    )
            for user_id, participant in now.items():
                if user_id not in was:
                    self.fire_participant_update(
                        UpdatedGroupCallParticipant(
                            self.chat_id,
                            GroupCallParticipant.Action.JOINED,
                            participant,
                        ),
                    )
                elif str(was[user_id]) != str(participant):
                    self.fire_participant_update(
                        UpdatedGroupCallParticipant(
                            self.chat_id,
                            GroupCallParticipant.Action.UPDATED,
                            participant,
                        ),
                    )

    def apply_call_fields(self, call):
        py_logger.debug(
            'Group Call Participants: Set from groupCall %d -> %d',
            self._version,
            call.version,
        )
        self._version = call.version or 1
        self._server_participants_count = call.participants_count
        self.schedule_date = call.schedule_date
        self.conference = bool(getattr(call, 'conference', False))
        self.messages_enabled = bool(getattr(call, 'messages_enabled', False))
        self.messages_min_price = (
            getattr(call, 'send_paid_messages_stars', None) or 0
        )
        self._all_participants_loaded = self._server_participants_count == len(
            self._participants
        )

    def apply_participants_slice(
        self,
        participants,
        slice_source: ApplySliceSource,
    ) -> list[UpdatedGroupCallParticipant]:
        updates = []
        for data in participants:
            user_id = BridgedClient.chat_id(data.peer)
            was = self._participants.get(user_id)
            if (
                data.left
                and was is not None
                and was.source == self.join_ssrc
                and data.source != self.join_ssrc
            ):
                continue
            if data.left:
                if was is not None:
                    self._participant_peer_by_audio_ssrc.pop(was.source, None)
                    self._apply_volume_from_min.discard(user_id)
                    del self._participants[user_id]
                updates.append(
                    UpdatedGroupCallParticipant(
                        self.chat_id,
                        GroupCallParticipant.Action.LEFT,
                        was or BridgedClient.parse_participant(data),
                    ),
                )
                if self._server_participants_count > 0:
                    self._server_participants_count -= 1
                continue
            value = BridgedClient.parse_participant(data)
            apply_volume_from_min = (
                user_id in self._apply_volume_from_min
                if was is not None and data.min
                else bool(data.min or data.volume_by_admin)
            )
            if was is not None and not apply_volume_from_min and data.min:
                value.volume = was.volume
            if apply_volume_from_min:
                self._apply_volume_from_min.add(user_id)
            else:
                self._apply_volume_from_min.discard(user_id)
            if was is not None and was.source != value.source:
                self._participant_peer_by_audio_ssrc.pop(was.source, None)
            if (
                was is not None
                and was.source != value.source
                and value.source != self.join_ssrc
            ):
                updates.append(
                    UpdatedGroupCallParticipant(
                        self.chat_id,
                        GroupCallParticipant.Action.KICKED,
                        was,
                    ),
                )
            if value.source:
                self._participant_peer_by_audio_ssrc[value.source] = user_id
            self._participants[user_id] = value
            if data.just_joined:
                self._server_participants_count += 1
            updates.append(
                UpdatedGroupCallParticipant(
                    self.chat_id,
                    GroupCallParticipant.Action.JOINED
                    if data.just_joined
                    or was is not None
                    and was.source != value.source
                    else GroupCallParticipant.Action.UPDATED,
                    value,
                ),
            )
        if slice_source != self.ApplySliceSource.UPDATE_RECEIVED:
            return []
        return updates

    async def apply_last_spoke(self, ssrcs: list[int]):
        self._unknown_spoken_ssrcs.update(
            ssrc
            for ssrc in ssrcs
            if ssrc not in self._participant_peer_by_audio_ssrc
        )
        await self.request_unknown_participants()

    async def request_unknown_participants(self):
        while (
            self._unknown_participant_peers_request is not None
            or self._unknown_spoken_ssrcs
        ):
            if self._unknown_participant_peers_request is not None:
                await self._unknown_participant_peers_request
                continue
            ssrcs = list(self._unknown_spoken_ssrcs)[: self.REQUEST_PER_PAGE]
            self._unknown_spoken_ssrcs.difference_update(ssrcs)
            request = asyncio.get_running_loop().create_future()
            self._unknown_participant_peers_request = request
            try:
                result = await self._app.get_group_participants(
                    self.input,
                    ssrcs,
                    '',
                    self.REQUEST_PER_PAGE,
                )
                self.apply_participants_slice(
                    result.participants,
                    self.ApplySliceSource.UNKNOWN_LOADED,
                )
            except Exception as e:
                py_logger.debug(
                    'Group Call Participants: Unknown failed: %s',
                    e,
                )
            finally:
                self._unknown_participant_peers_request = None
                request.set_result(None)

    def message_sending(self, random_id: int):
        self._sending_message_ids.add(random_id)

    def message_failed(self, random_id: int):
        self._sending_message_ids.discard(random_id)

    def message_sent(self, random_id: int, message_id: int) -> bool:
        if random_id not in self._sending_message_ids:
            return False
        self._sending_message_ids.discard(random_id)
        self._message_ids.add(message_id)
        return True

    async def message_received(self, data):
        if not self.loaded or self.conference:
            return
        if (
            data.id in self._message_ids
            or data.id in self._skipped_message_ids
        ):
            return
        message = BridgedClient.parse_group_call_message(data)
        if not message.text and message.stars < self.messages_min_price:
            self._skipped_message_ids.add(data.id)
            return
        self._message_ids.add(data.id)
        await self._app._propagate(
            UpdatedGroupCallMessage(
                self.chat_id,
                GroupCallMessage.Action.RECEIVED,
                data.id,
                message,
            ),
        )

    async def messages_deleted(self, message_ids: list[int]):
        if self.conference:
            return
        for message_id in message_ids:
            if message_id not in self._message_ids:
                continue
            self._message_ids.discard(message_id)
            await self._app._propagate(
                UpdatedGroupCallMessage(
                    self.chat_id,
                    GroupCallMessage.Action.DELETED,
                    message_id,
                ),
            )

    def conference_message_sent(self, random_id: int) -> int:
        self._conference_id_auto_increment += 1
        message_id = self._conference_id_auto_increment
        self._conference_id_by_random_id[random_id] = message_id
        return message_id

    async def encrypted_message_received(self, from_id, data: bytes):
        if (
            not self.loaded
            or not self.conference
            or self._app.e2e_decrypt is None
        ):
            return
        user_id = BridgedClient.chat_id(from_id)
        try:
            decrypted = await self._app.e2e_decrypt(
                self.chat_id,
                user_id,
                data,
            )
        except Exception as e:
            py_logger.debug('Group Call Messages: Decrypt failed: %s', e)
            return
        deserialized = BridgedClient.deserialize_conference_message(decrypted)
        if deserialized is None:
            py_logger.debug('Group Call Messages: Bad decrypted message')
            return
        random_id, text, entities = deserialized
        if random_id in self._conference_id_by_random_id:
            return
        message_id = self.conference_message_sent(random_id)
        await self._app._propagate(
            UpdatedGroupCallMessage(
                self.chat_id,
                GroupCallMessage.Action.RECEIVED,
                message_id,
                GroupCallMessage(
                    message_id,
                    user_id,
                    text,
                    BridgedClient.unparse_html(
                        text,
                        [self._app.message_entity(*e) for e in entities],
                    ),
                    int(time()),
                    0,
                    False,
                ),
            ),
        )
