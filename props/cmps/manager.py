"""Server Manager"""

import curses
from curses import window
from props.config import DEFAULT_PROFILE, DEFAULT_SYMLINK, PROFILE_DIR, SERVER_BIN
from props.errors import ReturnError
from props.osutils import (
    create_profile,
    create_symlink,
    get_active_version,
    list_versions,
)
from props.utility import prepare_windowed, windowed
from ..component import Component
from ..data import Colors, ReturnType, status


class Manager(Component):
    """Manage active version"""

    def __init__(self) -> None:
        super().__init__()
        status.reset()
        self._metadata = list_versions(str(SERVER_BIN))
        if self._metadata.type == ReturnType.ERR:
            raise ReturnError(self._metadata.reason)
        self._installed: list[str] = self._metadata.additional_info  # type: ignore
        self._current = get_active_version()
        self._select = 0

        self._key_events = {
            curses.KEY_UP: self.move_up,
            curses.KEY_DOWN: self.move_down,
            curses.KEY_LEFT: self.leave,
            curses.KEY_ENTER: self.select,
            10: self.select,
            curses.KEY_RIGHT: self.select
        }

    def select(self):
        """Select active function"""
        ver = self._installed[self._select]
        create_profile(ver)
        create_symlink(str(PROFILE_DIR / ver.replace(".jar", "")), str(DEFAULT_PROFILE))
        rt = create_symlink(str(SERVER_BIN / ver), str(DEFAULT_SYMLINK))
        status.set(rt.reason)
        return rt.type

    def move_up(self):
        """Move selection UP"""
        if self._select > 0:
            self._select -= 1
        return ReturnType.CONTINUE

    def move_down(self):
        """Move selection DOWN"""
        if self._select < len(self._installed) - 1:
            self._select += 1
        return ReturnType.CONTINUE

    def draw(self, stdscr: window) -> None | ReturnType:
        stdscr.addstr("Select PaperMC version to chose")

        minln, maxln = prepare_windowed(self._select, self.unreserved_lines)
        for idx, (rel_index, ver) in enumerate(windowed(self._installed, minln, maxln)):
            style = 0
            if rel_index == self._select:
                style = curses.color_pair(Colors.SELECTED)
            if ver == self._current:
                style = curses.color_pair(Colors.ACTIVE)

            stdscr.addstr(self.generic_height + idx, 0, f"-> {ver}", style)
