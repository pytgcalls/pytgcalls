import json

from aiohttp import web
from pyrogram.raw.functions.phone import JoinGroupCall
from pyrogram.raw.types import DataJSON
from pyrogram.raw.types import Updates


class JoinVoiceCall:
    def __init__(self, pytgcalls):
        self._pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    async def _join_voice_call(self, params: dict):
        request_call = {
            'ufrag': params['ufrag'],
            'pwd': params['pwd'],
            'fingerprints': [{
                'hash': params['hash'],
                'setup': params['setup'],
                'fingerprint': params['fingerprint'],
            }],
            'ssrc': params['source'],
        }
        chat_call = None
        # noinspection PyBroadException
        try:
            chat_call = await self._pytgcalls._load_chat_call(
                int(params['chat_id']),
            )
        except Exception:
            pass
        if chat_call is not None:
            try:
                result: Updates = await self._pytgcalls._app.send(
                    JoinGroupCall(
                        call=chat_call,
                        params=DataJSON(data=json.dumps(request_call)),
                        muted=False,
                        join_as=self._pytgcalls._cache_user_peer[
                            int(params['chat_id'])
                        ],
                        invite_hash=params['invite_hash'],
                    ),
                )
                transport = json.loads(result.updates[0].call.params.data)[
                    'transport'
                ]
                return web.json_response({
                    'transport': {
                        'ufrag': transport['ufrag'],
                        'pwd': transport['pwd'],
                        'fingerprints': transport['fingerprints'],
                        'candidates': transport['candidates'],
                    },
                })
            except Exception as e:
                if 'GROUPCALL_FORBIDDEN' in str(e):
                    if int(params['chat_id']) in \
                            self._pytgcalls._cache_full_chat:
                        del self._pytgcalls._cache_full_chat[
                            int(
                                params['chat_id'],
                            )
                        ]
                if self._pytgcalls._log_mode > 0:
                    print('JOIN_VOICE_CALL_ERROR ->', e)
        return web.json_response({'transport': None})
