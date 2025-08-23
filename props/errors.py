"""Errors"""
from .data import ReturnType

class ReturnError(Exception):
    """When a component failed to run during init"""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self._code = ReturnType.ERR

    @property
    def code(self):
        """ReturnType"""
        return self._code
