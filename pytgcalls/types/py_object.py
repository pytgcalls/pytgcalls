from enum import Enum
from json import dumps
from typing import Any
from typing import Dict
from typing import List
from typing import Union


class PyObject:
    @staticmethod
    def default(obj) -> Union[str, Dict[str, str], List[Any]]:
        if isinstance(obj, bytes):
            return repr(obj)
        if isinstance(obj, Enum):
            return repr(obj)
        return {
            '_': obj.__class__.__name__,
            **{
                attr: getattr(obj, attr)
                for attr in dir(obj)
                if not attr.startswith('_') and
                not callable(getattr(obj, attr)) and not attr == 'default'
            },
        }

    def __str__(self) -> str:
        return dumps(
            self,
            indent=4,
            default=self.default,
            ensure_ascii=False,
        )
