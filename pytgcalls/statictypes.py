from functools import wraps
from inspect import signature
from typing import Any
from typing import Union


def statictypes(func):
    sig = signature(func)

    def is_instance(obj, typ):
        origin = getattr(typ, '__origin__', None)
        if origin is Union:
            return any(is_instance(obj, t) for t in typ.__args__)
        elif origin in (list, set, tuple):
            if obj:
                return all(is_instance(x, typ.__args__[0]) for x in obj)
            return isinstance(obj, (list, set, tuple))
        elif origin is dict:
            if obj:
                return all(
                    is_instance(
                        x,
                        typ.__args__[0],
                    ) and is_instance(
                        obj[x],
                        typ.__args__[1],
                    ) for x in obj
                )
            return isinstance(obj, dict)
        return isinstance(obj, typ)

    def type_to_string(t):
        d = None
        if not hasattr(t, '__name__'):
            d = t
            t = type(t)
        origin = getattr(t, '__origin__', None)
        if origin in {list, dict, set, tuple}:
            return (
                t.__origin__.__name__.capitalize() + '['
                + ', '.join(type_to_string(tt) for tt in t.__args__) + ']'
            )

        if not d and t in {list, dict, set, tuple}:
            return t.__name__.capitalize()
        if t in {list, set, tuple}:
            inner_type = {type_to_string(k) for k in d}
            if not inner_type:
                return f'{t.__name__.capitalize()}'
            inner_type = 'Any' if len(
                inner_type,
            ) > 1 else list(inner_type)[0]
            return f'{t.__name__.capitalize()}[{inner_type}]'
        elif t is dict:
            key_type = {type_to_string(k) for k in d.keys()}
            value_type = {type_to_string(v) for v in d.values()}
            if not key_type or not value_type:
                return f'{t.__name__.capitalize()}'
            key_type = 'Any' if len(key_type) > 1 else list(key_type)[0]
            value_type = 'Any' if len(
                value_type,
            ) > 1 else list(value_type)[0]
            return f'{t.__name__.capitalize()}[{key_type}, {value_type}]'
        return t.__name__

    @wraps(func)
    def wrapper(*args, **kwargs):
        bound = sig.bind(*args, **kwargs)
        for name, value in bound.arguments.items():
            if name == 'self':
                continue
            expected_type = sig.parameters[name].annotation
            if expected_type is Any:
                continue
            types_expected = None
            if getattr(expected_type, '__origin__', None) is Union:
                tmp_types = expected_type.__args__
                if not any(is_instance(value, t) for t in tmp_types):
                    types_expected = ', '.join(
                        type_to_string(t) for t in tmp_types[:-1]
                    ) + ' or ' + type_to_string(tmp_types[-1])

            elif not isinstance(value, expected_type):
                types_expected = type_to_string(expected_type)

            if types_expected:
                raise TypeError(
                    f"Argument '{name}' has incorrect type. "
                    f'Expected {types_expected}, '
                    f"got '{type_to_string(value)}'",
                )
        return func(*args, **kwargs)

    return wrapper
