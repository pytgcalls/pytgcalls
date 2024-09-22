from enum import Enum
from json import dumps
from typing import Any
from typing import Dict
from typing import List
from typing import Union

class PyObject:
    @staticmethod
    def default(obj: Any) -> Union[str, Dict[str, Union[str, Any]], List[Any]]:
        if isinstance(obj, bytes):
            return repr(obj)
        if isinstance(obj, Enum):
            return obj.name 
        if hasattr(obj, '__dict__'):
            return {
                '_': obj.__class__.__name__,
                **{
                    attr: getattr(obj, attr) 
                    for attr in vars(obj)
                    if not attr.startswith('_')
                },
            }
        return {}

    def __str__(self) -> str:
        return dumps(
            self,
            indent=4,
            default=self.default,
            ensure_ascii=False,
        )
