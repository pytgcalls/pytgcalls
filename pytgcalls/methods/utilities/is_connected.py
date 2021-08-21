from ...scaffold import Scaffold


class IsConnected(Scaffold):
    @property
    def is_connected(self):
        return self._binding.is_alive()
