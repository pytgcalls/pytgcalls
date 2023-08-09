from ...scaffold import Scaffold


# TODO must be deleted
class IsConnected(Scaffold):
    @property
    def is_connected(self):
        return self._binding.is_alive()
