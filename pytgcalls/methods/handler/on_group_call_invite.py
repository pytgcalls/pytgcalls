from typing import Callable


class OnGroupCallInvite:
    def __init__(self, pytgcalls):
        self._pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    def on_group_call_invite(self) -> Callable:
        if (
                self._pytgcalls._app is not None
        ):
            method = 'GROUP_CALL_HANDLER'

            # noinspection PyProtectedMember
            def decorator(func: Callable) -> Callable:
                if self is not None:
                    self._pytgcalls._add_handler(
                        method, {
                            'callable': func,
                        },
                    )
                return func
        else:
            code_err = 'PYROGRAM_CLIENT_IS_NOT_RUNNING'
            raise Exception(f'Error internal: {code_err}')
        return decorator
