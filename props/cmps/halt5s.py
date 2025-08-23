"""Halt 5 second component... lmfao"""

# pylint: disable=no-member,no-name-in-module
from curses import window
from time import sleep

from props.curseutil import clear_line_yield
from props.data import ReturnType
from ..component import Component

class Halt5s(Component):
    """Halt for 5 seconds"""
    should_clear = False

    def draw(self, stdscr: window) -> None | ReturnType:
        with clear_line_yield(stdscr, self.height -1):
            stdscr.addstr(self.height -1, 0, "Waiting...")
            stdscr.refresh()
            sleep(5)
        return ReturnType.BACK
