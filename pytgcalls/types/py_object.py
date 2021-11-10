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
        if hasattr(obj, '__dict__'):
            return {
                '_': obj.__class__.__name__,
                **{
                    attr: vars(obj)[attr]
                    for attr in vars(obj)
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
