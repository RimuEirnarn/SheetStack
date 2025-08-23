"""Version Build Manager"""

from curses import window
import curses
from props.component import Component
from props.curseutil import clear_line_yield, hide_system
from props.paper import fetch_minecraft, fetch_version_info
from props.typings import VersionBuildRepo
from props.utility import prepare_windowed, windowed
from ..data import Colors, status, ReturnType, COMMON_TEXT


class BuildManager(Component):
    """Version Build component"""

    should_init = True
    generic_height = 3

    def __init__(self, version: str) -> None:
        super().__init__()
        status.reset()
        self._data: VersionBuildRepo = {}  # type: ignore
        self._select = 0
        self._version = version

        self._key_events = {
            curses.KEY_UP: self.move_up,
            curses.KEY_DOWN: self.move_down,
            curses.KEY_LEFT: self.leave,
            curses.KEY_ENTER: self.syscall,
            10: self.syscall,
            curses.KEY_RIGHT: self.syscall,
        }

    def syscall(self, stdscr: window):
        """Fetch PaperMC"""
        builds = tuple(reversed(self._data['builds']))
        build = builds[self._select]
        with hide_system(stdscr):
            print(f"Installing: PaperMC {self._version}/{build}")
            try:
                fetch_minecraft(self._version, build)
            except KeyboardInterrupt:
                status.set("Download aborted")
                return ReturnType.RETURN_TO_MAIN
            except Exception as exc: # pylint: disable=broad-exception-caught
                status.set(f"{type(exc).__name__}: {exc!s}")
                return ReturnType.ERR
            status.set(f"Installed PaperMC {self._version}-{build}")
        return ReturnType.RETURN_TO_MAIN

    def draw(self, stdscr: window) -> None | ReturnType:
        self.show_status(stdscr)
        stdscr.addstr(0, 0, COMMON_TEXT)
        builds = tuple(reversed(self._data["builds"]))
        build = builds[self._select]
        stdscr.addstr(
            1,
            0,
            (
                f"Selected: {self._version} / {build}. "
                "I recommend installing with newest build (usually with higher number)"
            ),
        )

        minln, maxln = prepare_windowed(self._select, self.unreserved_lines)
        for idx, (rel_index, build_info) in enumerate(windowed(builds, minln, maxln)):
            style = 0
            if rel_index == self._select:
                style = curses.color_pair(Colors.SELECTED)
            stdscr.addstr(self.generic_height + idx, 0, f"-> {build_info}", style)

    def move_up(self):
        """Move UP"""
        if self._select > 0:
            self._select -= 1
        return ReturnType.CONTINUE

    def move_down(self):
        """Move DOWN"""
        if self._select < len(self._data["builds"]) - 1:
            self._select += 1
        return ReturnType.CONTINUE

    def init(self, stdscr: window):
        if self._init:
            return

        with clear_line_yield(stdscr, self.height - 1):
            stdscr.addstr(self.height - 1, 0, "Fetching repository list")
            stdscr.refresh()
            self._data = fetch_version_info(self._version)

        self._init = True
