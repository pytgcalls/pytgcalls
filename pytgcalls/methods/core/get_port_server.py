class GetPortServer:
    def __init__(self, pytgcalls):
        self.pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    def get_port_server(self):
        return self.pytgcalls._port
