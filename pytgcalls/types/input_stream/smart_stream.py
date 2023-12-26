from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from ...media_devices import DeviceInfo
from ...media_devices import ScreenInfo
from .audio_parameters import AudioParameters
from .stream import Stream
from .video_parameters import VideoParameters


class SmartStream(Stream):
    def __init(self):
        self._audio_data: Tuple[
            str,
            Union[str, ScreenInfo, DeviceInfo],
            AudioParameters,
            List[str],
            Optional[Dict[str, str]],
        ]
        self._video_data: Tuple[
            str,
            Union[str, ScreenInfo, DeviceInfo],
            VideoParameters,
            List[str],
            Optional[Dict[str, str]],
        ]
        pass

    async def check_stream(self):
        pass
