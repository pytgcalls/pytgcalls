from Naked.toolshed.shell import execute_js


class RunJS:
    def __init__(self, pytgcalls):
        self.pytgcalls = pytgcalls

    # noinspection PyBroadException
    def _run_js(
        self,
        file_path: str = '',
        arguments: str = '',
    ):
        try:
            execute_js(file_path, arguments)
        except KeyboardInterrupt:
            self.is_running = False
            print(
                f'\n{self.pytgcalls.FAIL} '
                f'NodeJS Core Stopped, '
                f'press Ctrl+C again to exit!'
                f'{self.pytgcalls.ENDC}',
            )
