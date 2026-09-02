from enum import Enum
from json import dumps
from typing import Any


class PyObject:
    @staticmethod
    def default(obj) -> str | dict[str, str] | list[Any]:
        if isinstance(obj, bytes):
            return repr(obj)
        elif isinstance(obj, Enum):
            return ' | '.join(
                [f'{obj.__class__.__name__}.{x}' for x in obj.name.split('|')],
            )
        return {
            '_': obj.__class__.__name__,
            **{
                attr: getattr(obj, attr)
                for attr in dir(obj)
                if not attr.startswith('_')
                and not callable(getattr(obj, attr))
                and not attr == 'default'
            },
        }

    def __str__(self) -> str:
        return dumps(
            self,
            indent=4,
            default=self.default,
            ensure_ascii=False,
        )
