from time import time

from ...scaffold import Scaffold


class Ping(Scaffold):
    @property
    def ping(self) -> float:
        start_time: float = time()
        self._binding.ping()

        return round((time() - start_time) * 1000.0, 5)
