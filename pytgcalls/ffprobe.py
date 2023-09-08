from typing import Dict
from typing import List
from typing import Optional


# TODO refactor needed
class FFprobe:
    @staticmethod
    def ffmpeg_headers(
            headers: Optional[Dict[str, str]] = None,
    ):
        ffmpeg_params: List[str] = []
        if headers is not None:
            ffmpeg_params.append('-headers')
            built_header = ''
            for i in headers:
                built_header += f'{i}: {headers[i]}\r\n'
            ffmpeg_params.append(built_header)
        return ':_cmd_:'.join(
            ffmpeg_params,
        )
