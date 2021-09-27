from typing import Union, Dict
from json import dumps


class PyObject:
    @staticmethod
    def default(obj) -> Union[str, Dict[str, str]]:
        if isinstance(obj, bytes):
            return repr(obj)
        return {
            "_": obj.__class__.__name__,
            **{
                attr: vars(obj)[attr]
                for attr in vars(obj)
            }
        }

    def __str__(self) -> str:
        return dumps(self, indent=4, default=self.default, ensure_ascii=False)
