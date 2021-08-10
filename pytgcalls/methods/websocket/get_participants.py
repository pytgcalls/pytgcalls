from aiohttp import web
from pyrogram.raw.functions.phone import GetGroupParticipants
from pyrogram.raw.types.phone import GroupParticipants


class GetParticipants:
    def __init__(self, pytgcalls):
        self._pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    async def _get_participants(self, params: dict):
        participants: GroupParticipants = (
            await self._pytgcalls._app.send(
                GetGroupParticipants(
                    call=await self._pytgcalls._load_chat_call(
                        params['chat_id'],
                    ),
                    ids=[],
                    sources=[],
                    offset='',
                    limit=5000,
                ),
            )
        )
        return web.json_response([
            {'source': x.source, 'user_id': x.peer.user_id}
            for x in participants.participants
        ])
