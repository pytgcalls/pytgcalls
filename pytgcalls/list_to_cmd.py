import platform
import shlex
import subprocess
from typing import List


def list_to_cmd(args: List[str]) -> str:
    if platform.system() == 'Windows':
        return subprocess.list2cmdline(args)
    else:
        return shlex.join(args)
