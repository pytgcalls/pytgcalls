from sys import platform


class DeviceInfo:
    def __init__(
        self,
        identifier: str,
        title: str,
    ):
        self.identifier = identifier
        self.title = title
        self.ffmpeg_parameters = ['-f']

    def build_ffmpeg_command(self):
        if platform == 'win32':
            self.ffmpeg_parameters += ['dshow']
            return f'audio={self.identifier}'
        else:
            self.ffmpeg_parameters += ['pulse']
        return self.identifier
