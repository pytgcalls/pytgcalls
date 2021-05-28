from collections import Callable
import threading


class SpawnProcess:
    @staticmethod
    def _spawn_process(function: Callable, args=()):
        t1 = threading.Thread(target=function, args=args)
        t1.start()
