from sys import platform

from ..types.py_object import PyObject


class ScreenInfo(PyObject):
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        is_primary: bool,
        title: str,
    ):
        self.offset_x = x
        self.offset_y = y
        self.width = width
        self.height = height
        self.is_primary = is_primary
        self.title = title
        self.ffmpeg_parameters = ''

    def build_ffmpeg_command(self, frame_rate: int):
        if platform == 'win32':
            path = 'desktop'
            self.ffmpeg_parameters = '-f gdigrab '
            self.ffmpeg_parameters += f'-offset_x {self.offset_x} '
            self.ffmpeg_parameters += f'-offset_y {self.offset_y} '
        else:
            path = f':0.0+{self.offset_x},{self.offset_y}'
            self.ffmpeg_parameters = '-f x11grab '
        self.ffmpeg_parameters += f'-video_size {self.width}x{self.height} '
        self.ffmpeg_parameters += f'-framerate {frame_rate}'
        return path
