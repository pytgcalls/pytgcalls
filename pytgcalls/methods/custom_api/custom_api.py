from . import CustomAPIHelpers
from ..core import env


class CustomAPI(CustomAPIHelpers):
    def __init__(self):
        if env.custom_api_instance is None:
            env.custom_api_instance = self
            self._custom_api_handler = None
        else:
            raise Exception(
                'You cannot use more than one CustomApi instance',
            )
        super().__init__(self)
