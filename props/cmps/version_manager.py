"""Version Group Manager"""

from curses import window
import curses
from props.typings import GlobalRepo
from props.utility import prepare_windowed, windowed
from ..component import Component, MenuComponent
from ..data import Colors, status, ReturnType, COMMON_TEXT
from .build_manager import BuildManager

class VersionManager(MenuComponent):
    """Version manager"""

    should_init = False

    def __init__(self, selected: str, data: GlobalRepo) -> None:
        super().__init__()
        # self._data: GlobalRepo = {} # type: ignore
        self._verlist = tuple(
            filter(lambda ver: ver.startswith(selected), data["versions"])
        )
        self._selected = selected
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
        stdscr.addstr(1, 0, f"Selected: {self._selected}")

        minln, maxln = prepare_windowed(self._select, self.unreserved_lines)
        for idx, (rel_index, version) in enumerate(
            windowed(self._verlist, minln, maxln)
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
        if self._select < len(self._verlist) - 1:
            self._select += 1
        return ReturnType.CONTINUE

    def call(self) -> Component | ReturnType:
        return BuildManager(self._verlist[self._select])
