import logging
from typing import Optional

from pyrogram import Client
from pyrogram.raw.functions.channels import GetFullChannel
from pyrogram.raw.types import InputGroupCall

from .types import Cache


class PyroCache:
    def __init__(
        self,
        cache_duration: int,
        app: Client,
    ):
        self._app = app
        self._cache_duration = cache_duration
        self._full_chat_cache = Cache()

    async def get_full_chat(
        self,
        chat_id: int,
    ) -> Optional[InputGroupCall]:
        full_chat = self._full_chat_cache.get(chat_id)
        if full_chat is not None:
            logging.debug('FullChat cache hit for %d', chat_id)
            return full_chat
        else:
            # noinspection PyBroadException
            try:
                logging.debug('FullChat cache miss for %d', chat_id)
                chat = await self._app.resolve_peer(chat_id)
                full_chat = (
                    await self._app.send(
                        GetFullChannel(channel=chat),
                    )
                ).full_chat.call
                self.set_cache(
                    chat_id,
                    full_chat,
                )
                return full_chat
            except Exception:
                pass
        return None

    def set_cache(
        self,
        chat_id: int,
        input_call: InputGroupCall,
    ) -> None:
        self._full_chat_cache.put(
            chat_id,
            input_call,
            self._cache_duration,
        )

    def drop_cache(
        self,
        chat_id,
    ) -> None:
        self._full_chat_cache.pop(chat_id)
