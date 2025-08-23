"""Main component"""

# pylint: disable=no-member,no-name-in-module

import curses
from curses import window
from typing import Type

from ..osutils import get_active_version
from ..data import ReturnType, status, Colors
from ..component import Component, MenuComponent

from .version_group import VersionGroupManager
from .manager import Manager
from .server import Server
from .shell import Shell
from .halt5s import Halt5s
from .help import Help
from .app_exit import Exit

ENTRIES: list[tuple[str, Type[Component]]] = [
    ("Install new version", VersionGroupManager),
    ("Select version", Manager),
    ("Run", Server),
    ("Shell", Shell),
    ("Help", Help),
    ("Halt 5s", Halt5s),
    ("Exit", Exit),
]


class Root(MenuComponent):
    """Root component"""
    generic_height = 3

    def __init__(self) -> None:
        super().__init__()
        self._key_events = {
            curses.KEY_UP: self.move_up,
            curses.KEY_DOWN: self.move_down,
            curses.KEY_ENTER: self.call,
            curses.KEY_RIGHT: self.call,
            10: self.call
        }
        self._select = 0

    def draw(self, stdscr: window):
        version = get_active_version()
        if version:
            stdscr.addstr(
                0,
                0,
                "Manage your Minecraft version (↑↓ to navigate, Enter/Right to select):",
            )
        if version:
            stdscr.addstr(1, 0, f"Current server version: {version}")
        stdscr.addstr(self.height - 1, 0, status.get())

        for idx, (label, _) in enumerate(ENTRIES):
            style = 0
            if idx == self._select:
                style = curses.color_pair(Colors.SELECTED)

            stdscr.addstr(self.generic_height + idx, 0, f'-> {label}\n', style)

    def move_up(self):
        """Move selection UP"""
        if self._select > 0:
            self._select -= 1
        return ReturnType.CONTINUE

    def move_down(self):
        """Move selection DOWN"""
        if self._select < len(ENTRIES) - 1:
            self._select += 1
        return ReturnType.CONTINUE

    def call(self) -> Component | ReturnType:
        """Call and return a component"""
        component = ENTRIES[self._select][1]()
        if isinstance(component, Exit):
            return ReturnType.EXIT
        return component
