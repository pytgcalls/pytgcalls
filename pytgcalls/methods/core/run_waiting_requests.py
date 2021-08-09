import builtins

import requests


class RunWaitingRequests:
    def __init__(self, pytgcalls):
        self.pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    @staticmethod
    def _run_waiting_requests():
        for instance in builtins.client_instances:
            if instance.is_running:
                for req in instance._waiting_start_request:
                    req[0](*req[1])
