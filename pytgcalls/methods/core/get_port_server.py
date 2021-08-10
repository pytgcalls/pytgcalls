class GetPortServer:
    def __init__(self, pytgcalls):
        self._pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    def get_port_server(self):
        return self._pytgcalls._port
