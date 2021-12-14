import json

import requests
from pyrogram import Client
from pyrogram import filters
from pyrogram.types import Message

from pytgcalls import CustomApi
from pytgcalls import idle

app = Client(
    'py-tgcalls',
    api_id=123456789,
    api_hash='abcdef12345',
)

ca = CustomApi()


# Useful for making requests for bots in PHP
# with Webhooks or bots in different programming language
@ca.on_update_custom_api()
async def custom_api_request(request: dict):
    print(request)
    return {
        'response': 'BYE',
    }


@app.on_message(filters.regex('!test'))
def test_handler(client: Client, message: Message):
    print(
        requests.post(
            'http://localhost:24859/', json.dumps({
                'answer': 'HI',
            }),
        ).json(),
    )


app.start()
ca.start()
idle()
