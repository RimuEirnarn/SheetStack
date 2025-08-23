"""Curses utility"""

# pylint: disable=no-member

from os import get_terminal_size
import curses
from contextlib import contextmanager

@contextmanager
def hide_system(stdscr: curses.window):
    """Hide the app UI to parent TTY"""
    curses.endwin()
    try:
        yield
    finally:
        stdscr.refresh()
        curses.doupdate()

def clear_line(stdscr: curses.window, line: int):
    """Clear a line"""
    stdscr.addstr(line, 0, " " * (get_terminal_size().columns - 1))

@contextmanager
def clear_line_yield(stdscr: curses.window, line: int):
    """Clear line through context var"""
    clear_line(stdscr, line)
    try:
        yield
    finally:
        clear_line(stdscr, line)
        stdscr.refresh()
