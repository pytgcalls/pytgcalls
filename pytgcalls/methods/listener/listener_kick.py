from pyrogram import Client
from pyrogram.raw.types import GroupCallDiscarded
from pyrogram.raw.types import InputGroupCall
from pyrogram.raw.types import UpdateChannel
from pyrogram.raw.types import UpdateGroupCall
from pyrogram.raw.types import UpdateGroupCallParticipants


class ListenerKick:
    def __init__(self, app_tg: Client, context, my_id: int):
        self.chat_id = 0

        @app_tg.on_raw_update()
        async def on_close(client, update, data1, data2):
            if isinstance(update, UpdateChannel):
                self.chat_id = int(f'-100{update.channel_id}')
            if isinstance(update, UpdateGroupCallParticipants):
                if isinstance(update.call, InputGroupCall):
                    if (
                        update.participants[0].user_id == my_id and
                        update.participants[0].left and
                        self.chat_id != 0
                    ):
                        context.leave_group_call(
                            self.chat_id, 'kicked_from_group',
                        )
                        self.chat_id = 0
            if isinstance(update, UpdateGroupCall):
                if isinstance(update.call, GroupCallDiscarded):
                    context.leave_group_call(int(f'-100{update.chat_id}'))
