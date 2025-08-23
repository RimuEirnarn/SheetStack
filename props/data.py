"""Data-related information"""

from enum import IntEnum
from typing import NamedTuple, Generic, TypeVar

T = TypeVar("T")

class ReturnType(IntEnum):
    """Return type"""

    OK = 0
    ERR = 1
    RETURN_TO_MAIN = 2
    BACK = 3
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
