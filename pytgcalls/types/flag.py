from enum import Flag as _Flag

from .py_object import PyObject


class Flag(PyObject, _Flag):
    pass
