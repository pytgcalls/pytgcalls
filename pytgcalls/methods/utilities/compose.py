import asyncio

from ... import PyTgCalls
from .idle import idle


async def compose(
    clients: list[PyTgCalls],
    sequential: bool = False,
):
    if sequential:
        for c in clients:
            await c.start()
    else:
        await asyncio.gather(*[c.start() for c in clients])

    await idle()
