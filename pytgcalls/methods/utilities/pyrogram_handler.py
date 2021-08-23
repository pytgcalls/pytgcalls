from typing import Dict

from pyrogram import ContinuePropagation
from pyrogram.raw.types import Channel
from pyrogram.raw.types import ChannelForbidden
from pyrogram.raw.types import GroupCall
from pyrogram.raw.types import GroupCallDiscarded
from pyrogram.raw.types import InputGroupCall
from pyrogram.raw.types import MessageActionInviteToGroupCall
from pyrogram.raw.types import MessageService
from pyrogram.raw.types import UpdateChannel
from pyrogram.raw.types import UpdateGroupCall
from pyrogram.raw.types import UpdateNewChannelMessage

from ...scaffold import Scaffold


class PyrogramHandler(Scaffold):
    async def _init_pyrogram(self):
        if not self._app.is_connected:
            await self._app.start()
        self._my_id = (await self._app.get_me())['id']
        self._cache_local_peer = await self._app.resolve_peer(
            self._my_id,
        )

    def _handle_pyrogram(self):
        @self._app.on_raw_update()
        async def on_pyro_update(_, update, __, data2):
            if isinstance(
                update,
                UpdateGroupCall,
            ):
                if isinstance(
                    update.call,
                    GroupCall,
                ):
                    self._full_chat_cache.set_cache(
                        int(f'-100{update.chat_id}'),
                        InputGroupCall(
                            access_hash=update.call.access_hash,
                            id=update.call.id,
                        ),
                    )
                if isinstance(
                    update.call,
                    GroupCallDiscarded,
                ):
                    chat_id = int(f'-100{update.chat_id}')
                    self._full_chat_cache.drop_cache(chat_id)
                    self._cache_user_peer.pop(chat_id)
                    await self._binding.send({
                        'action': 'leave_call',
                        'chat_id': chat_id,
                        'type': 'closed_voice_chat',
                    })
                    await self._on_event_update.propagate(
                        'CLOSED_HANDLER',
                        self,
                        chat_id,
                    )
            if isinstance(
                update,
                UpdateChannel,
            ):
                chat_id = int(f'-100{update.channel_id}')
                if len(data2) > 0:
                    if isinstance(
                        data2[update.channel_id],
                        ChannelForbidden,
                    ):
                        self._call_holder.remove_call(
                            chat_id,
                        )
                        await self._binding.send({
                            'action': 'leave_call',
                            'chat_id': chat_id,
                            'type': 'kicked_from_group',
                        })
                        await self._on_event_update.propagate(
                            'KICK_HANDLER',
                            self,
                            chat_id,
                        )
                        self._cache_user_peer.pop(chat_id)
            if isinstance(
                update,
                UpdateNewChannelMessage,
            ):
                if isinstance(
                    update.message,
                    MessageService,
                ):
                    if isinstance(
                        update.message.action,
                        MessageActionInviteToGroupCall,
                    ):
                        await self._on_event_update.propagate(
                            'INVITE_HANDLER',
                            self,
                            update.message.action,
                        )
            if isinstance(
                data2,
                Dict,
            ):
                for channel_id in data2:
                    if isinstance(
                        update,
                        UpdateNewChannelMessage,
                    ):
                        if isinstance(
                            update.message,
                            MessageService,
                        ):
                            if isinstance(
                                data2[channel_id],
                                Channel,
                            ):
                                if data2[channel_id].left:
                                    await self._on_event_update.propagate(
                                        'LEFT_HANDLER',
                                        self,
                                        int(f'-100{channel_id}'),
                                    )
            raise ContinuePropagation()
