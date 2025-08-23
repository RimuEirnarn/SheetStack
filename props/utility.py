"""Utility"""

from typing import Type, Callable, TypeVar
from functools import wraps

from .data import status, ReturnType

T = TypeVar("T")

def clear_info():
    """erase status info"""
    status.reset()

def supress(exclist: tuple[Type[BaseException], ...] | list[Type[BaseException]]):
    """Surpress incoming errors"""

    def outer(fn: Callable[..., ReturnType]):
        @wraps(fn)
        def inner(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except BaseException as exc:  # type: ignore # pylint: disable=broad-exception-caught
                if not type(exc) in exclist:
                    raise
                status.set(f"{type(exc).__name__}: {exc!s}")
                return ReturnType.ERR

        return inner

    return outer


def windowed(data: list[T] | tuple[T, ...], start: int, end: int):
    """Return an enumerated, windowed list based on start and end.
    Start/end must incorporated values returned by prepare_windowed"""
    return list(enumerate(data))[start:end]


def prepare_windowed(index: int, visible_rows: int):
    """Return min/max length for windowed function"""
    minln = max(0, index - (visible_rows // 2))
    maxln = (
        visible_rows if index <= (visible_rows // 2) else (index + visible_rows // 2)
    )
    return minln, maxln
