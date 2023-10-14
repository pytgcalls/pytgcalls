from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from .audio_parameters import AudioParameters
from .stream import Stream
from .video_parameters import VideoParameters


class SmartStream(Stream):
    def __init(self):
        self._audio_data: Tuple[
            str,
            str,
            AudioParameters,
            List[str],
            Optional[Dict[str, str]],
        ]
        self._video_data: Tuple[
            str,
            str,
            VideoParameters,
            List[str],
            Optional[Dict[str, str]],
        ]
        pass

    async def check_stream(self):
        pass
