from aiohttp import web
from pyrogram.raw.functions.phone import EditGroupCallParticipant


class ChangeVolumeVoiceCall:
    def __init__(self, pytgcalls):
        self._pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    async def _change_volume_voice_call(self, params: dict):
        # noinspection PyBroadException
        try:
            chat_call = await self._pytgcalls._load_chat_call(
                params['chat_id'],
            )
            await self._pytgcalls._app.send(
                EditGroupCallParticipant(
                    call=chat_call,
                    participant=self._pytgcalls._cache_user_peer[
                        int(params['chat_id'])
                    ],
                    muted=False,
                    volume=params['volume'] * 100,
                ),
            )
        except Exception:
            pass
        return web.json_response({
            'result': 'OK',
        })
