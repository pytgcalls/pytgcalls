from enum import Flag as _Flag


class Flag(_Flag):
    def __repr__(self):
        return f'{self.__class__.__name__}.{self.name}'
