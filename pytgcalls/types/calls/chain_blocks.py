from typing import List


class ChainBlocks:
    def __init__(
        self,
        sub_chain_id: int,
        blocks: List[bytes],
        next_offset: int,
    ):
        self.sub_chain_id = sub_chain_id
        self.blocks = blocks
        self.next_offset = next_offset
