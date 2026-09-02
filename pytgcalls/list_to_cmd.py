import platform
import shlex
import subprocess


def list_to_cmd(args: list[str]) -> str:
    if platform.system() == 'Windows':
        return subprocess.list2cmdline(args)
    else:
        return shlex.join(args)
