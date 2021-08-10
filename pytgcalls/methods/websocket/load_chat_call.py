from time import time

from pyrogram.raw.functions.channels import GetFullChannel
from pyrogram.raw.types.messages import ChatFull


class LoadChatCall:
    def __init__(self, pytgcalls):
        self._pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    async def _load_chat_call(self, chat_id: int) -> ChatFull:
        curr_time = int(time())
        load_cache = False
        if chat_id in self._pytgcalls._cache_full_chat:
            if curr_time - self._pytgcalls._cache_full_chat[
                chat_id
            ]['last_update'] < self._pytgcalls._flood_wait_cache:
                load_cache = True
        if load_cache:
            full_chat = self._pytgcalls._cache_full_chat[
                chat_id
            ]['full_chat']
        else:
            chat = await self._pytgcalls._app.resolve_peer(chat_id)
            full_chat = (
                await self._pytgcalls._app.send(
                    GetFullChannel(channel=chat),
                )
            ).full_chat.call
            self._pytgcalls._cache_full_chat[chat_id] = {
                'last_update': curr_time,
                'full_chat': full_chat,
            }
        if self._pytgcalls._log_mode > 1:
            print(
                'Pyrogram -> GetFullChannel',
                f'executed with {"cache" if load_cache else "Telegram"}',
            )
        return full_chat
