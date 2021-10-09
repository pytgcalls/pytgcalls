from math import gcd

from pytgcalls.exceptions import InvalidVideoProportion
from pytgcalls.types.input_stream.quality import HighQualityVideo
from pytgcalls.types.input_stream.quality import LowQualityVideo
from pytgcalls.types.input_stream.quality import MediumQualityVideo
from pytgcalls.types.input_stream.video_parameters import VideoParameters


def check_support(link: str):
    supported_protocols = [
        'https://',
        'http://',
        'rtmp://',
    ]
    return any(
        protocol in link
        for protocol in supported_protocols
    )


def check_video_params(
    video_params: VideoParameters,
    dest_width: int,
    dest_height: int,
):
    def resize_ratio(w, h, factor):
        if w > h:
            rescaling = ((1280 if w > 1280 else w) * 100) / w
        else:
            rescaling = ((720 if h > 720 else h) * 100) / h
        h = round((h * rescaling) / 100)
        w = round((w * rescaling) / 100)
        divisor = gcd(w, h)
        ratio_w = w / divisor
        ratio_h = h / divisor
        factor = (divisor * factor) / 100
        return round(ratio_w * factor), round(ratio_h * factor)

    height = video_params.height
    width = video_params.width
    if isinstance(
        video_params,
        HighQualityVideo,
    ):
        width, height = resize_ratio(dest_width, dest_height, 100)
    if isinstance(
        video_params,
        MediumQualityVideo,
    ):
        width, height = resize_ratio(dest_width, dest_height, 66.69)
    if isinstance(
        video_params,
        LowQualityVideo,
    ):
        width, height = resize_ratio(dest_width, dest_height, 50)
    if dest_height < height:
        raise InvalidVideoProportion(
            'Destination height is greater than the original height',
        )
    width = width - 1 if width % 2 else width
    height = height - 1 if height % 2 else height
    return width, height
