from sys import platform


class DeviceInfo:
    def __init__(
        self,
        identifier: str,
        title: str,
    ):
        self.identifier = identifier
        self.title = title
        self.ffmpeg_parameters = ''

    def build_ffmpeg_command(self):
        if platform == 'win32':
            self.ffmpeg_parameters = '-f dshow'
            return f'audio={self.identifier}'
        else:
            self.ffmpeg_parameters = '-f pulse'
        return self.identifier
