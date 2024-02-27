import asyncio
from typing import List

from ... import PyTgCalls
from .idle import idle


async def compose(
    clients: List[PyTgCalls],
    sequential: bool = False,
):
    if sequential:
        for c in clients:
            await c.start()
    else:
        await asyncio.gather(*[c.start() for c in clients])

    await idle()
