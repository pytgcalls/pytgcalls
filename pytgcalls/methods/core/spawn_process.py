import threading
from collections import Callable


class SpawnProcess:
    @staticmethod
    def _spawn_process(function: Callable, args=()):
        t1 = threading.Thread(target=function, args=args)
        t1.start()
