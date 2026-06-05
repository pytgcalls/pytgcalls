from typing import TypeVar

from ..types.py_object import PyObject

T = TypeVar('T')
U = TypeVar('U')


class Dict(PyObject, dict[T, U]):
    pass
