from ..update import Update
from .chain_blocks import ChainBlocks


class ChainBlocksUpdate(Update):
    def __init__(
        self,
        chat_id: int,
        chain_blocks: ChainBlocks,
    ):
        super().__init__(chat_id)
        self.chain_blocks = chain_blocks
