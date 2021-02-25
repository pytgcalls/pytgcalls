from pyrogram.raw.functions.channels import GetFullChannel
from pyrogram.raw.types.messages import ChatFull


class LoadFullChat:
    def __init__(self, pytgcalls):
        self.pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    async def _load_full_chat(self, chat_id: int) -> ChatFull:
        chat = await self.pytgcalls._app.resolve_peer(chat_id)
        full_chat = await self.pytgcalls._app.send(
            GetFullChannel(channel=chat),
        )
        return full_chat
