"""Data-related information"""

from enum import IntEnum
from typing import NamedTuple, Generic, TypeVar

T = TypeVar("T")

COMMON_TEXT = (
    "Please install which version you wish to install"
    "(↑↓ to navigate, Enter to select, Left/Right to undo/select)"
)

class ReturnType(IntEnum):
    """Return type"""

    OK = 0
    ERR = 1
    RETURN_TO_MAIN = 2
    BACK = 3
    CONTINUE = 4
    EXIT = -1


class Colors(IntEnum):
    """Colros"""

    ACTIVE = 1
    SELECTED = 2

    NOT_INSTALLED = 3

class ReturnInfo(Generic[T], NamedTuple):
    """Return info"""
    type: ReturnType
    reason: str
    additional_info: T

class _StatusInfo:
    def __init__(self) -> None:
        self._data = " "

    def get(self) -> str:
        return self._data

    def set(self, value: str):
        self._data = value

    def reset(self):
        self._data = " "

status = _StatusInfo()
