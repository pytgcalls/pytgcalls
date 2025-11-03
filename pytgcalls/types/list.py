from typing import TypeVar

from ..types.py_object import PyObject


T = TypeVar('T')


class List(PyObject, list[T]):
    pass
