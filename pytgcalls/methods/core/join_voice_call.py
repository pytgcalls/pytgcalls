import json
import logging

from pyrogram.raw.functions.phone import JoinGroupCall
from pyrogram.raw.types import DataJSON
from pyrogram.raw.types import UpdateGroupCall
from pyrogram.raw.types import Updates

from ...scaffold import Scaffold


class JoinVoiceCall(Scaffold):
    async def _join_voice_call(
        self,
        params: dict,
    ):
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
        chat_id = int(params['chat_id'])
        chat_call = await self._full_chat_cache.get_full_chat(
            chat_id,
        )
        if chat_call is not None:
            try:
                result: Updates = await self._app.send(
                    JoinGroupCall(
                        call=chat_call,
                        params=DataJSON(data=json.dumps(request_call)),
                        muted=False,
                        join_as=self._cache_user_peer.get(chat_id),
                        invite_hash=params['invite_hash'],
                    ),
                )
                for update in result.updates:
                    if isinstance(update, UpdateGroupCall):
                        transport = json.loads(update.call.params.data)[
                            'transport'
                        ]
                        return {
                            'transport': {
                                'ufrag': transport['ufrag'],
                                'pwd': transport['pwd'],
                                'fingerprints': transport['fingerprints'],
                                'candidates': transport['candidates'],
                            },
                        }
            except Exception as e:
                if 'GROUPCALL_FORBIDDEN' in str(e):
                    self._full_chat_cache.drop_cache(chat_id)
                    self._cache_user_peer.pop(chat_id)
                logging.error(f'JOIN_VOICE_CALL_ERROR -> {e}')
        return {'transport': None}
