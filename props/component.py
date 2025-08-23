"""Component base class module"""
# pylint: disable=no-member,unused-import,unused-argument
from inspect import signature
import curses
from os import get_terminal_size
from typing import Callable, TypeAlias, TypeIs

from .data import ReturnType

DefaultCallback: TypeAlias = "Callable[[], ReturnType | Component]"
WinCallback: TypeAlias = "Callable[[curses.window], ReturnType]"

def uses_window(fn: "DefaultCallback | WinCallback") -> TypeIs[WinCallback]:
    """Check if a function uses a window param"""
    fn_signature = signature(fn)
    return 'stdscr' in fn_signature.parameters

class Component:
    """Base class for all sorts of components"""
    generic_height: int = 2
    reserved_lines: int = 5
    should_clear: bool = True
    should_init: bool = False

    """Your main component"""
    def __init__(self) -> None:
        self._key_events: "dict[int, DefaultCallback | WinCallback]" = {}
        self._init = False

    def draw(self, stdscr: curses.window) -> None | ReturnType:
        """Draw this component"""
        raise NotImplementedError

    def handle_key(self, key: int, stdscr: curses.window) -> "ReturnType | Component":
        """Handle key component"""
        if key == 'q': # SHOULD NOT OVERRIDE
            return ReturnType.EXIT
        fn = self._key_events.get(key, None)
        if callable(fn):
            if uses_window(fn):
                return fn(stdscr)
            return fn() # type: ignore
        return ReturnType.CONTINUE

    def syscall(self, stdscr: curses.window) -> ReturnType:
        """Do whatever you want."""
        return ReturnType.OK

    def leave(self):
        """Leave this component"""
        return ReturnType.BACK

    def init(self, stdscr: curses.window):
        """Initialize this component"""
        return None

    @property
    def term_size(self):
        """Return terminal size"""
        return get_terminal_size()

    @property
    def height(self):
        """Height of current terminal"""
        return self.term_size.lines

    @property
    def width(self):
        """Width of current terminal"""
        return self.term_size.columns

    @property
    def unreserved_lines(self):
        """Return unreserved lines"""
        return self.height - self.reserved_lines

class MenuComponent(Component):
    """Menu component"""
    def __init__(self) -> None:
        super().__init__()
        self._select = 0

    def call(self) -> "Component | ReturnType":
        """Call a component"""
        raise NotImplementedError

    def move_up(self):
        """Move the selection UP"""
        raise NotImplementedError

    def move_down(self):
        """Move the selection DOWN"""
        raise NotImplementedError
