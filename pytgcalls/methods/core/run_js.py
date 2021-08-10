import subprocess
import sys


class RunJS:
    def __init__(self, pytgcalls):
        self._pytgcalls = pytgcalls

    # noinspection PyBroadException
    def _run_js(
        self,
        file_path: str = '',
        arguments: str = '',
    ):
        try:
            self._execute(f'node {file_path} {arguments}')
        except KeyboardInterrupt:
            self.is_running = False
            self.is_connected = False

    @staticmethod
    def _execute(command):
        try:
            response = subprocess.call(command, shell=True)
            if response == 0:
                return True
            else:
                return False
        except subprocess.CalledProcessError as cpe:
            try:
                sys.stderr.write(cpe.output)
            except TypeError:
                sys.stderr.write(str(cpe.output))
        except Exception as e:
            raise e
