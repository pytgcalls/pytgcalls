import json

from aiohttp import web
from aiohttp.web_request import BaseRequest
from pyrogram.raw.functions.phone import GetGroupParticipants
from pyrogram.raw.types.phone import GroupParticipants


class GetPartecipants:
    def __init__(self, pytgcalls):
        self.pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    async def _get_participants(self, request: BaseRequest):
        params = await request.json()
        if isinstance(params, str):
            params = json.loads(params)
        participants: GroupParticipants = (
            await self.pytgcalls._app.send(
                GetGroupParticipants(
                    call=(
                        await self.pytgcalls._load_full_chat(
                            params['chat_id'],
                        )
                    ).full_chat.call,
                    ids=[],
                    sources=[],
                    offset='',
                    limit=5000,
                ),
            )
        )
        return web.json_response([
            {'source': x.source, 'user_id': x.user_id}
            for x in participants.participants
        ])
