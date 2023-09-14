import shlex


def build_ffmpeg_command(
    ffmpeg_parameters: str,
    path: str,
    stream_type: str,
    stream_parameters,
) -> str:
    command = _get_stream_params(ffmpeg_parameters).get(stream_type)

    before_i: str = ' '.join(command.get('start', ''))
    after_i: str = ' '.join(command.get('mid', ''))
    at_end: str = ' '.join(command.get('end', ''))
    frame_rate: int = stream_parameters.frame_rate

    ffmpeg_command: list = [
        'ffmpeg ',
        f'{before_i} ' if before_i else '',
    ]

    if stream_type == 'image':
        frame_rate = 1
        ffmpeg_command.append(f'-loop 1 -framerate {frame_rate} ')

    if stream_type == 'video' or stream_type == 'image':
        ffmpeg_command.append(f'-i {path} ')
        ffmpeg_command.append(
            f'{after_i} -f rawvideo ' if after_i else '-f rawvideo ',
        )
        ffmpeg_command.append(
            f'-r {frame_rate} -pix_fmt yuv420p -vf '
            f'scale={stream_parameters.width}:{stream_parameters.height} ',
        )
    else:
        ffmpeg_command.append(f'-i {path} ')
        ffmpeg_command.append(
            f'{after_i} -f s16le ' if after_i else '-f s16le ',
        )
        ffmpeg_command.append(
            f'-ac {stream_parameters.channels} '
            f'-ar {stream_parameters.bitrate} ',
        )

    ffmpeg_command.append(f'{at_end} pipe:1' if at_end else 'pipe:1')

    return ''.join(ffmpeg_command)


def _get_stream_params(command: str):
    arg_names = ['base', 'audio', 'video']
    command_args: dict = {arg: [] for arg in arg_names}
    current_arg = arg_names[0]

    for part in shlex.split(command):
        arg_name = part[2:]
        if arg_name in arg_names:
            current_arg = arg_name
        else:
            command_args[current_arg].append(part)

    command_args = {
        command: _extract_stream_params(command_args[command])
        if command_args[command] else [] for command in command_args
    }

    command_args = {
        command: command_args[command]
        if command_args[command] else command_args[arg_names[0]]
        for command in command_args
    }
    del command_args[arg_names[0]]

    return command_args


def _extract_stream_params(command: list[str]):
    arg_names = ['start', 'mid', 'end']
    command_args: dict = {arg: [] for arg in arg_names}
    current_arg = arg_names[0]

    for part in command:
        arg_name = part[3:]
        if arg_name in arg_names:
            current_arg = arg_name
        else:
            command_args[current_arg].append(part)

    return command_args
