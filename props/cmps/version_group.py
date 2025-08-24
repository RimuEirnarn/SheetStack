"""Version Group Manager"""

from curses import window
import curses
from props.component import Component
from props.curseutil import clear_line_yield
from props.paper import fetch_global
from props.typings import GlobalRepo
from props.utility import prepare_windowed, windowed
from ..component import MenuComponent
from ..data import Colors, status, ReturnType, COMMON_TEXT
from .version_manager import VersionManager


class VersionGroupManager(MenuComponent):
    """Version group component"""

    should_init = True

    def __init__(self) -> None:
        super().__init__()
        self._data: GlobalRepo = {}  # type: ignore
        status.reset()

        self._key_events = {
            curses.KEY_UP: self.move_up,
            curses.KEY_DOWN: self.move_down,
            curses.KEY_LEFT: self.leave,
            curses.KEY_ENTER: self.call,
            10: self.call,
            curses.KEY_RIGHT: self.call,
        }

    def draw(self, stdscr: window) -> None | ReturnType:
        stdscr.addstr(0, 0, COMMON_TEXT)

        minln, maxln = prepare_windowed(self._select, self.unreserved_lines)
        for idx, (rel_index, version) in enumerate(
            windowed(self._data["version_groups"], minln, maxln)
        ):
            style = 0
            if rel_index == self._select:
                style = curses.color_pair(Colors.SELECTED)
            stdscr.addstr(self.generic_height + idx, 0, f"-> {version}", style)

    def move_up(self):
        if self._select > 0:
            self._select -= 1
        return ReturnType.CONTINUE

    def move_down(self):
        if self._select < len(self._data["version_groups"]) - 1:
            self._select += 1
        return ReturnType.CONTINUE

    def call(self) -> Component | ReturnType:
        return VersionManager(self._data["version_groups"][self._select], self._data)

    def init(self, stdscr: window):
        if self._init:
            return

        with clear_line_yield(stdscr, self.height - 1):
            stdscr.addstr(self.height - 1, 0, "Fetching repository list")
            stdscr.refresh()
            self._data = fetch_global()

        self._init = True
