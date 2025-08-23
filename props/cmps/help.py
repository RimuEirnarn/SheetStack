"""App help component"""
# pylint: disable=no-member

import curses

from ..data import ReturnType
from ..component import Component


class Help(Component):
    """Help component"""

    def __init__(self) -> None:
        super().__init__()
        self._key_events = {curses.KEY_LEFT: lambda: ReturnType.BACK}

    def draw(self, stdscr: curses.window):
        stdscr.addstr(
            0,
            0,
            "You can install PaperMC, select the default version, or run the server.",
        )
        stdscr.addstr(1, 0, "Use [LEFT] to go back.")
