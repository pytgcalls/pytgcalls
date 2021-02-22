from collections import Callable
from multiprocessing.context import Process


class SpawnProcess:
    @staticmethod
    def _spawn_process(function: Callable, args=()):
        p = Process(target=function, args=args)
        p.start()
        return p
